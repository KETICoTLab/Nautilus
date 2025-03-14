# individual contribution method


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



def nt_get_client_information(results):
    
    client_training_result_data = []
    
    for _result in results:
        tmp_meta = _result.meta
        tmp_client_name = tmp_meta.get("client_name", AppConstants.CLIENT_UNKNOWN)
        tmp_current_round = tmp_meta.get("NUM_STEPS_CURRENT_ROUND")
        tmp_accuracy = tmp_meta.get("accuracy")
        tmp_metric = tmp_meta.get("metric")
        
        tmp_append_data_list = [tmp_client_name, tmp_current_round, tmp_accuracy, tmp_metric]
        client_training_result_data.append(tmp_append_data_list)
    
    return client_training_result_data

def nt_calculate_client_contrib_total(res):
    # norm client contrib
    total_contrib = 0
    for tmp_res in res:
        total_contrib += tmp_res[2]
    return total_contrib


def nt_calculate_client_contrib(data, mode = None):
    # nautilus contrib estimation method
    # mode is calculate client contrib expression method
    # norm : client contrib calculation -> 0 ~ 1
    # acc : client contrib estimation via accuacy -> 78, 85, ...
    # loss : client contrib estimation via loss -> 0.322, 0.112, ...
    # reverse : client contrib estimation via reverse -> 5,4,3,2,1
    # rank : client contrib estimation via rank -> 1,2,3,4,5 
    mode_list = ['norm', 'acc', 'loss', 'reverse', 'rank']

    client_contrib_res = {}
    
    if mode == '' or mode == None:
        mode = 'acc'
        print('[Nautilus SYS] : Mode is not defined, Set Accuracy Mode')

    if mode not in mode_list:
        print('Error : mode is not defined')
    
    if mode == 'norm':
        #norm mode
        tmp_total = nt_calculate_client_contrib_total(data)
        sorted_data = sorted(data, key=lambda x: x[2], reverse=True)
        for idx, res in enumerate(sorted_data):
            tmp_client_name = res[0]
            tmp_client_acc = res[2]
            tmp_client_norm = tmp_client_acc/tmp_total
            client_contrib_res[idx+1] = [tmp_client_name, tmp_client_norm]
        
        print('here client contrib_ res : ',client_contrib_res)
        return client_contrib_res
        
        
    elif mode == 'acc':
        # acc mode
        sorted_data = sorted(data, key=lambda x: x[2], reverse=True)
        for idx, res in enumerate(sorted_data):
            tmp_client_name = res[0]
            tmp_client_acc = res[2]
            
            client_contrib_res[idx+1] = [tmp_client_name,tmp_client_acc]
        
        print('here client contrib_ res : ',client_contrib_res)
        return client_contrib_res

    elif mode == 'loss':
        # loss mode
        sorted_data = sorted(data, key=lambda x: x[3])
        for idx, res in enumerate(sorted_data):
            tmp_client_name = res[0]
            tmp_client_metric = res[3]
            
            client_contrib_res[idx+1] = [tmp_client_name, tmp_client_metric]
        print('here client contrib_ res : ',client_contrib_res)
        return client_contrib_res
    elif mode == 'reverse':
        # reverse mode
        sorted_data = sorted(data, key=lambda x: x[2])
        for idx, res in enumerate(sorted_data):
            tmp_client_name = res[0]
            tmp_client_acc = res[2]

            client_contrib_res[idx+1] = [tmp_client_name, tmp_client_acc]
        print('here client contrib_ res : ',client_contrib_res)
        return client_contrib_res

    elif mode == 'rank':
        # rank mode
        sorted_data = sorted(data, key=lambda x: x[2], reverse=True)
        for idx, res in enumerate(sorted_data):
            tmp_client_name = res[0]
            tmp_client_acc = res[2]
            
            client_contrib_res[idx+1] = [tmp_client_name,idx+1]
        
        print('here client contrib_ res : ',client_contrib_res)
        return client_contrib_res



def nt_contrib_individual(results, mode=None):
    # client training result decomposition
    # client data generation
    client_training_result_data = nt_get_client_information(results)
    client_contrib_res = nt_calculate_client_contrib(client_training_result_data, mode)

    return client_contrib_res


