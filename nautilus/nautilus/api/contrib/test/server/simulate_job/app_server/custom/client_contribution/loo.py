# leave-one-out (loo) contribution evaluation method


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

        
        tmp_client_append_data = [tmp_client_name, tmp_accuracy, tmp_param, tmp_data_size]
        
        client_training_result_data.append(tmp_client_append_data)
    
    return client_training_result_data

def nt_calculate_client_contrib_total(res):
    total_contrib = 0
    for tmp_res in res:
        total_contrib += tmp_res[-1]
    return total_contrib

def nt_calculate_avg_model(client_data):
    num_clients = len(client_data)
    avg_params = {k: torch.zeros_like(v) for k, v in client_data[0][2].items()}

    for client in client_data:
        for k, param in client[2].items(): 
            avg_params[k] += param / num_clients
    
    return avg_params

def nt_make_client_combination_avg_model(client_data):
    # Nautilus client combination average model
    # client_data : [client_name, accuracy, param, data_size]
    # This function is to make client combination average model
    client_combination_avg_model = []
    for i in range(len(client_data)):
        now_client_name = client_data[i][0]
        tmp_client_data_list = client_data[:i] + client_data[i+1:]
        tmp_avg_model = nt_calculate_avg_model(tmp_client_data_list)
        client_combination_avg_model.append([now_client_name,tmp_avg_model])
    return client_combination_avg_model

def nt_calculate_test_accuracy(model, model_weight, DEVICE, test_data):
    test_model = model
    test_model.load_state_dict(model_weight)
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



def nt_calculate_client_leave_one_out(model, client_data, DEVICE, test_data):
    total_avg_model = nt_calculate_avg_model(client_data)
    client_combination_avg_model = nt_make_client_combination_avg_model(client_data)

    total_model_accuracy = nt_calculate_test_accuracy(model, total_avg_model, DEVICE, test_data)
    loo_comparision_list = []
    
    for client in client_combination_avg_model:
        client_name = client[0]
        client_accuracy = nt_calculate_test_accuracy(model, client[1], DEVICE, test_data)
        diff_accuracy = total_model_accuracy - client_accuracy
        loo_comparision_list.append([client_name, diff_accuracy])
    
    sorted_loo_comparision_list = sorted(loo_comparision_list, key = lambda x: x[1])

    client_contrib_res = {}
    for idx, res in enumerate(sorted_loo_comparision_list):
        client_contrib_res[idx+1] = [res[0], res[1]]

    return client_contrib_res



def nt_contrib_loo(initial_model, results, DEVICE, test_data, mode = None):
    # nautilus contrib estimation method
    # basic : client contribution evaluation via leave one out (Even weight)
    # weighted : client contribution evaluation via weighted 

    mode_list = ['basic','weighted']

    client_contrib_res = {}
    
    if mode == '' or mode == None:
        mode = 'basic'
        print('[Nautilus SYS] : Mode is not defined, Set Basic Mode')
    
    if mode not in mode_list:
        print('[ Nautilus SYS ] : Error : mode is not defined')
    
    if mode == 'basic':
        # basic mode
        client_data = nt_get_client_information(results)
        client_model = initial_model
        client_contrib_res = nt_calculate_client_leave_one_out(client_model, client_data, DEVICE, test_data)
        print('loo result :', client_contrib_res)
        return client_contrib_res
    
            