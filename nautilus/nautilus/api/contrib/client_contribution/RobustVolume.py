# Robust Volume Contribution

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
from scipy.spatial import ConvexHull
from sklearn.decomposition import PCA


def nt_get_feature_embeddings(results):
    client_data = []
    for res in results:
        meta = res.meta
        name = meta.get("client_name", AppConstants.CLIENT_UNKNOWN)
        embedding = meta.get("feature_embedding")
        data_size = meta.get("data_size", 1)
        if embedding:
            emb = np.array(embedding)
            client_data.append((name, emb, data_size))
    return client_data

def reduce_feature_dim(features, dim=10):
    pca = PCA(n_components=dim)
    return pca.fit_transform(features)

def calculate_volume(embeddings):
    if len(embeddings) < embeddings.shape[1] + 1:
        return 0.0
    try:
        hull = ConvexHull(embeddings)
        print('hull.volume', hull.volume)
        return hull.volume
    except:
        return 0.0

def nt_contrib_robust_volume(results):
    client_data = nt_get_feature_embeddings(results)
    all_points = np.vstack([cd[1] for cd in client_data])
    reduced_all = reduce_feature_dim(all_points, dim=10)

    idx = 0
    volume_map = {}
    pointer = 0
    for name, emb, _ in client_data:
        num = emb.shape[0]
        volume_map[name] = reduced_all[pointer:pointer+num]
        pointer += num

    total_volume = calculate_volume(reduced_all)

    contrib_scores = {}
    for name, _emb, _ in client_data:
        other_points = np.vstack([v for k, v in volume_map.items() if k != name])
        volume_without = calculate_volume(other_points)
        contrib_scores[name] = max(total_volume - volume_without, 0)

    total = sum(contrib_scores.values())
    print('total', total)
    for k in contrib_scores:
        contrib_scores[k] = contrib_scores[k] / total if total > 0 else 0

    print("[RobustVolume Scores]", contrib_scores)
    return contrib_scores


'''
def nt_get_feature_embeddings(results):
    client_data = []
    for res in results:
        meta = res.meta
        name = meta.get("client_name", AppConstants.CLIENT_UNKNOWN)
        embedding = meta.get("feature_embedding")
        data_size = meta.get("data_size", 1)
        if embedding:
            emb = np.array(embedding)
            client_data.append((name, emb, data_size))
    return client_data

def calculate_volume(embeddings):
    if len(embeddings) < 4:
        return 0.0  # ConvexHull requires at least D+1 points in D-dim space
    try:
        print('now here')
        hull = ConvexHull(embeddings)
        print('hull.volume', hull.volume)
        return hull.volume
    except:
        return 0.0

def nt_contrib_robust_volume(results):
    client_data = nt_get_feature_embeddings(results)
    all_points = np.vstack([cd[1] for cd in client_data])
    total_volume = calculate_volume(all_points)

    contrib_scores = {}
    for name, emb, _ in client_data:
        other_points = np.vstack([cd[1] for cd in client_data if cd[0] != name])
        volume_without = calculate_volume(other_points)
        contrib_scores[name] = max(total_volume - volume_without, 0)
    
    print("volume (all points):", total_volume)
    print("volume (without X):", volume_without)

    total = sum(contrib_scores.values())
    print('total', total)
    for k in contrib_scores:
        contrib_scores[k] = contrib_scores[k] / total if total > 0 else 0

    print("[RobustVolume Scores]", contrib_scores)
    return contrib_scores'
'''
