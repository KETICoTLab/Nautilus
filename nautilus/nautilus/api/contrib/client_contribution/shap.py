# shap contribution evaluation method


from typing import List, Optional

import torch.nn as nn

import gc
import random
from abc import ABC, abstractmethod
from typing import Callable, List, Union
from nvflare.app_common.abstract.model_locator import ModelLocator
from nvflare.app_common.abstract.model_persistor import ModelPersistor
from nvflare.app_common.tracking.tracker_types import ANALYTIC_EVENT_TYPE
from nvflare.app_common.widgets.convert_to_fed_event import ConvertToFedEvent
from nvflare.app_common.widgets.intime_model_selector import IntimeModelSelector
from nvflare.app_common.widgets.streaming import AnalyticsReceiver
from nvflare.app_common.widgets.validation_json_generator import ValidationJsonGenerator
from nvflare.app_opt.pt.job_config.model import PTModel
from nvflare.app_opt.tracking.tb.tb_receiver import TBAnalyticsReceiver
from nvflare.job_config.api import FedJob, validate_object_for_job
from nvflare.apis.fl_constant import FLMetaKey
from nvflare.app_common.abstract.fl_model import FLModel
from nvflare.app_common.abstract.model import make_model_learnable
from nvflare.app_common.aggregators.weighted_aggregation_helper import WeightedAggregationHelper
from nvflare.app_common.app_constant import AppConstants

from nvflare.app_common.utils.fl_model_utils import FLModelUtils
from nvflare.security.logging import secure_format_exception

from typing import Callable, List, Union

from nvflare.app_common.abstract.fl_model import FLModel
from nvflare.app_common.app_constant import AppConstants

from nvflare.apis.client import Client
from nvflare.apis.controller_spec import ClientTask, OperatorMethod, Task, TaskOperatorKey
from nvflare.apis.fl_constant import ReturnCode
from nvflare.apis.fl_context import FLContext
from nvflare.apis.impl.controller import Controller
from nvflare.apis.shareable import Shareable
from nvflare.apis.signal import Signal
from nvflare.app_common.abstract.fl_model import FLModel, ParamsType
from nvflare.app_common.abstract.learnable_persistor import LearnablePersistor
from nvflare.app_common.abstract.model import ModelLearnable, ModelLearnableKey, make_model_learnable
from nvflare.app_common.app_constant import AppConstants
from nvflare.app_common.app_event_type import AppEventType
from nvflare.app_common.utils.fl_component_wrapper import FLComponentWrapper
from nvflare.app_common.utils.fl_model_utils import FLModelUtils
from nvflare.fuel.utils.validation_utils import check_non_negative_int, check_positive_int, check_str
from nvflare.security.logging import secure_format_exception

from nvflare.app_opt.pt.job_config.base_fed_job import BaseFedJob
import torch
import numpy as np
import itertools
from math import factorial

def nt_get_client_information(results):
    # loo client_information

    client_training_result_data = []

    for _result in results:
        tmp_meta = _result.meta
        tmp_client_name = tmp_meta.get("client_name", AppConstants.CLIENT_UNKNOWN)
        tmp_accuracy = tmp_meta.get("accuracy")
        tmp_param = _result.params
        tmp_data_size = tmp_meta.get("data_size")

        if isinstance(tmp_param, dict):
            tmp_param = {k: torch.tensor(v) if isinstance(v, np.ndarray) else v for k, v in tmp_param.items()}

        # client_name, accuracy, param, data_size
        tmp_client_append_data = [tmp_client_name, tmp_accuracy, tmp_param, tmp_data_size]
        
        client_training_result_data.append(tmp_client_append_data)
    
    return client_training_result_data

def nt_calculate_test_accuracy(model, model_weight, DEVICE, test_data):
    test_model = model
    model_weight_tensor = {k: torch.tensor(v) for k, v in model_weight.items()}
    test_model.load_state_dict(model_weight_tensor)
    test_model.to(DEVICE)

    correct = 0
    total = 0

    with torch.no_grad():
        for data in test_data:
            images, labels = data[0].to(DEVICE), data[1].to(DEVICE)
            outputs = test_model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    return 100 * correct / total

def create_client_combination(client_result_data):
    client_combination = []
    for r in range(1, len(client_result_data)+1):
        combos = list(itertools.combinations(client_result_data, r))
        
        client_combination.extend(combos)
    return client_combination

def nt_calculate_client_combination_accuracy(initial_model, client_combination, DEVICE, test_data):
    comb_params = {k: torch.zeros_like(v) for k, v in client_combination[0][2].items()}
    div_len = len(client_combination)
    client_list = []
    for client in client_combination:
        for k, param in client[2].items():
            comb_params[k] += param/div_len
        client_list.append(client[0])
    res = nt_calculate_test_accuracy(initial_model, comb_params, DEVICE, test_data)
    #print([client_list, res])
    return [client_list, res]
    
def nt_calculate_avg_contrib(total_data):
    performance_dict = {tuple(sorted(sites)): perf for sites, perf in total_data}
    all_sites = set()
    for sites, _ in total_data:
        all_sites.update(sites)
    all_sites = sorted(list(all_sites))
    n = len(all_sites)
    def shapley_value(target_site, all_sites, performance_dict):
        phi = 0.0
        N = set(all_sites)
        for r in range(0, n):  
            for S in itertools.combinations(N - {target_site}, r):
                S = set(S)
                S_with_i = tuple(sorted(S | {target_site}))
                S_tuple = tuple(sorted(S))
                v_S = performance_dict.get(S_tuple, 0)
                v_S_with_i = performance_dict.get(S_with_i, 0)
                weight = factorial(len(S)) * factorial(n - len(S) - 1) / factorial(n)
                phi += weight * (v_S_with_i - v_S)
        return phi
    shapley_scores = {}
    for site in all_sites:
        shapley_scores[site] = shapley_value(site, all_sites, performance_dict)
    return shapley_scores


def nt_contrib_shap(initial_model, results, DEVICE, test_data, mode = None):
    # Nautilus shap contribution evaluation method
    mode_list = ['basic','weighted']

    #client_contrib_res = {}
    
    if mode == '' or mode == None:
        mode = 'basic'
        print('[Nautilus SYS] : Mode is not defined, Set Basic Mode')
    
    if mode not in mode_list:
        print('[ Nautilus SYS ] : Error : mode is not defined')
    
    if mode == 'basic':
        # basic mode
        client_data = nt_get_client_information(results)
        comb_list = create_client_combination(client_data)
        total_data = []
        for comb in comb_list:
            tmp_res = nt_calculate_client_combination_accuracy(initial_model, comb, DEVICE, test_data)
            total_data.append(tmp_res)
        shap_score = nt_calculate_avg_contrib(total_data)
        print(shap_score)
        return shap_score
    
