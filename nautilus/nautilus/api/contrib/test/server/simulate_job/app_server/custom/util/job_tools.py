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
import torchvision
import torch
import torchvision.transforms as transforms

from nvflare.app_opt.pt.job_config.base_fed_job import BaseFedJob

class nt_model_controller(Controller, FLComponentWrapper, ABC):
    def __init__(
        self,
        persistor_id: str = AppConstants.DEFAULT_PERSISTOR_ID,
        ignore_result_error: bool = False,
        allow_empty_global_weights: bool = False,
        task_check_period: float = 0.5,
    ):

        super().__init__(task_check_period=task_check_period)

        # Check arguments
        check_str("persistor_id", persistor_id)
        if not isinstance(task_check_period, (int, float)):
            raise TypeError(f"task_check_period must be an int or float but got {type(task_check_period)}")
        elif task_check_period <= 0:
            raise ValueError("task_check_period must be greater than 0.")
        self._task_check_period = task_check_period
        self._persistor_id = persistor_id
        self.persistor = None

        # config data
        self._ignore_result_error = ignore_result_error
        self._allow_empty_global_weights = allow_empty_global_weights

        # model related
        self._results = []

    def start_controller(self, fl_ctx: FLContext) -> None:
        self.fl_ctx = fl_ctx
        self.info("Initializing nautilus model contol workflow.")

        self.engine = self.fl_ctx.get_engine()

        if self._persistor_id:
            self.persistor = self.engine.get_component(self._persistor_id)
            if not isinstance(self.persistor, LearnablePersistor):
                self.warning(
                    f"Persistor {self._persistor_id} must be a LearnablePersistor type object, "
                    f"but got {type(self.persistor)}"
                )
                self.persistor = None

        FLComponentWrapper.initialize(self)

    def _build_shareable(self, data: FLModel = None) -> Shareable:
        data_shareable: Shareable = FLModelUtils.to_shareable(data)
        data_shareable.add_cookie(
            AppConstants.CONTRIBUTION_ROUND, data_shareable.get_header(AppConstants.CURRENT_ROUND)
        )

        return data_shareable

    def broadcast_model(
        self,
        data,
        task_name: str = AppConstants.TASK_TRAIN,
        targets: Union[List[Client], List[str], None] = None,
        min_responses: int = None,
        timeout: int = 0,
        wait_time_after_min_received: int = 0,
        blocking: bool = True,
        callback: Callable[[FLModel], None] = None,
    ) -> List:

        if not isinstance(task_name, str):
            raise TypeError(f"task_name must be a string but got {type(task_name)}")
        if not isinstance(data, FLModel):
            raise TypeError(f"data must be a FLModel but got {type(data)}")
        if min_responses is None:
            min_responses = 0  # this is internally used by controller's broadcast to represent all targets
        check_non_negative_int("min_responses", min_responses)
        check_non_negative_int("timeout", timeout)
        check_non_negative_int("wait_time_after_min_received", wait_time_after_min_received)
        if not blocking and not isinstance(callback, Callable):
            raise TypeError("callback must be defined if blocking is False, but got {}".format(type(callback)))

        self.set_fl_context(data)

        task = self._prepare_task(data=data, task_name=task_name, timeout=timeout, callback=callback)

        if targets:
            targets = [client.name if isinstance(client, Client) else client for client in targets]
            self.info(f"Sending task {task_name} to {targets}")
        else:
            self.info(f"Sending task {task_name} to all clients")

        if blocking:
            self._results = []  # reset results list
            self.broadcast_and_wait(
                task=task,
                targets=targets,
                min_responses=min_responses,
                wait_time_after_min_received=wait_time_after_min_received,
                fl_ctx=self.fl_ctx,
                abort_signal=self.abort_signal,
            )

            if targets is not None:
                expected_responses = min_responses if min_responses != 0 else len(targets)
                if len(self._results) != expected_responses:
                    self.warning(
                        f"Number of results ({len(self._results)}) is different from number of expected responses ({expected_responses})."
                    )

            # de-reference the internal results before returning
            results = self._results
            self._results = []
            return results
        else:
            self.broadcast(
                task=task,
                targets=targets,
                min_responses=min_responses,
                wait_time_after_min_received=wait_time_after_min_received,
                fl_ctx=self.fl_ctx,
            )

    def _prepare_task(
        self,
        data: FLModel,
        task_name: str,
        timeout: int,
        callback: Callable,
    ):
        # Create task
        data_shareable = self._build_shareable(data)

        operator = {
            TaskOperatorKey.OP_ID: task_name,
            TaskOperatorKey.METHOD: OperatorMethod.BROADCAST,
            TaskOperatorKey.TIMEOUT: timeout,
        }

        task = Task(
            name=task_name,
            data=data_shareable,
            operator=operator,
            props={AppConstants.TASK_PROP_CALLBACK: callback, AppConstants.META_DATA: data.meta},
            timeout=timeout,
            before_task_sent_cb=self._prepare_task_data,
            result_received_cb=self._process_result,
        )

        return task

    def _prepare_task_data(self, client_task: ClientTask, fl_ctx: FLContext) -> None:
        fl_ctx.set_prop(AppConstants.TRAIN_SHAREABLE, client_task.task.data, private=True, sticky=False)
        self.event(AppEventType.BEFORE_TRAIN_TASK)

    def _process_result(self, client_task: ClientTask, fl_ctx: FLContext) -> None:
        self.fl_ctx = fl_ctx
        result = client_task.result
        client_name = client_task.client.name

        # Turn result into FLModel
        # here is make meta data : Accuracy, Training_metric etc...
        result_model = FLModelUtils.from_shareable(result)
        result_model.meta["props"] = client_task.task.props[AppConstants.META_DATA]
        result_model.meta["client_name"] = client_name

        self.event(AppEventType.BEFORE_CONTRIBUTION_ACCEPT)
        self._accept_train_result(client_name=client_name, result=result, fl_ctx=fl_ctx)
        self.event(AppEventType.AFTER_CONTRIBUTION_ACCEPT)

        callback = client_task.task.get_prop(AppConstants.TASK_PROP_CALLBACK)
        if callback:
            try:
                callback(result_model)
            except Exception as e:
                self.error(f"Unsuccessful callback {callback} for task {client_task.task.name}: {e}")
        else:
            self._results.append(result_model)

            # Cleanup task result
            client_task.result = None

        gc.collect()

    def process_result_of_unknown_task(
        self, client: Client, task_name: str, client_task_id: str, result: Shareable, fl_ctx: FLContext
    ) -> None:
        if task_name == AppConstants.TASK_TRAIN:
            self._accept_train_result(client_name=client.name, result=result, fl_ctx=fl_ctx)
            self.info(f"Result of unknown task {task_name} sent to aggregator.")
        else:
            self.error("Ignoring result from unknown task.")

    def _accept_train_result(self, client_name: str, result: Shareable, fl_ctx: FLContext):
        self.fl_ctx = fl_ctx
        rc = result.get_return_code()

        current_round = result.get_header(AppConstants.CURRENT_ROUND, None)

        # Raise panic if bad peer context or execution exception.
        if rc and rc != ReturnCode.OK:
            if self._ignore_result_error:
                self.warning(
                    f"Ignore the train result from {client_name} at round {current_round}. Train result error code: {rc}",
                )
            else:
                self.panic(
                    f"Result from {client_name} is bad, error code: {rc}. "
                    f"{self.__class__.__name__} exiting at round {current_round}."
                )
                return

        self.fl_ctx.set_prop(AppConstants.TRAINING_RESULT, result, private=True, sticky=False)

    @abstractmethod
    def run(self):
        raise NotImplementedError

    def control_flow(self, abort_signal: Signal, fl_ctx: FLContext) -> None:
        self.fl_ctx = fl_ctx
        self.abort_signal = abort_signal
        try:
            self.info("Beginning model controller run.")
            self.event(AppEventType.TRAINING_STARTED)

            self.run()
        except Exception as e:
            error_msg = f"Exception in model controller run: {secure_format_exception(e)}"
            self.exception(error_msg)
            self.panic(error_msg)

    def load_model(self):
        # initialize global model
        model = None
        if self.persistor:
            self.info("loading initial model from persistor")
            global_weights = self.persistor.load(self.fl_ctx)

            if not isinstance(global_weights, ModelLearnable):
                self.panic(
                    f"Expected global weights to be of type `ModelLearnable` but received {type(global_weights)}"
                )
                return

            if global_weights.is_empty():
                if not self._allow_empty_global_weights:
                    # if empty not allowed, further check whether it is available from fl_ctx
                    global_weights = self.fl_ctx.get_prop(AppConstants.GLOBAL_MODEL)

            if not global_weights.is_empty():
                model = FLModel(
                    params_type=ParamsType.FULL,
                    params=global_weights[ModelLearnableKey.WEIGHTS],
                    meta=global_weights[ModelLearnableKey.META],
                )
            elif self._allow_empty_global_weights:
                model = FLModel(params_type=ParamsType.FULL, params={})
            else:
                self.panic(
                    f"Neither `persistor` {self._persistor_id} or `fl_ctx` returned a global model! If this was intended, set `self._allow_empty_global_weights` to `True`."
                )
                return
        else:
            self.info("persistor not configured, creating empty initial FLModel")
            model = FLModel(params_type=ParamsType.FULL, params={})

        # persistor uses Learnable format to save model
        ml = make_model_learnable(weights=model.params, meta_props=model.meta)
        self.fl_ctx.set_prop(AppConstants.GLOBAL_MODEL, ml, private=True, sticky=True)
        self.event(AppEventType.INITIAL_MODEL_LOADED)

        return model

    def get_run_dir(self):
        return self.engine.get_workspace().get_run_dir(self.fl_ctx.get_job_id())

    def get_app_dir(self):
        return self.engine.get_workspace().get_app_dir(self.fl_ctx.get_job_id())

    def save_model(self, model):
        if self.persistor:
            self.info("Start persist model on server.")
            self.event(AppEventType.BEFORE_LEARNABLE_PERSIST)
            # persistor uses Learnable format to save model
            ml = make_model_learnable(weights=model.params, meta_props=model.meta)
            self.persistor.save(ml, self.fl_ctx)
            self.event(AppEventType.AFTER_LEARNABLE_PERSIST)
            self.info("End persist model on server.")
        else:
            self.error("persistor not configured, model will not be saved")

    def sample_clients(self, client_list) -> List[str]:
        clients = [client.name for client in self.engine.get_clients()]
        # ex) [1,3,5,7] -> ['site-1','site-3','site-5','site-7']
        if client_list == []:
            return clients
        ret_cli_list = []

        if max(client_list) > len(clients)-1:
            self.info('Error - client selection error : num_of_clients < sample_client')

        for idx in client_list:
            ret_cli_list.append(clients[idx])
        self.info(f"Sampled clients: {ret_cli_list}")

        return ret_cli_list


    def set_fl_context(self, data: FLModel):
        """Set up the fl_ctx information based on the passed in FLModel data."""
        if data and data.current_round is not None:
            self.fl_ctx.set_prop(AppConstants.CURRENT_ROUND, data.current_round, private=True, sticky=True)
        else:
            self.debug("The FLModel data does not contain the current_round information.")

    def get_component(self, component_id: str):
        return self.engine.get_component(component_id)

    def build_component(self, config_dict: dict):
        return self.engine.build_component(config_dict)

    def stop_controller(self, fl_ctx: FLContext):
        self.fl_ctx = fl_ctx
        self.finalize()


class nt_Model_Control_Pack(nt_model_controller, ABC):
    def __init__(
        self,
        *args,
        persistor_id: str = AppConstants.DEFAULT_PERSISTOR_ID,
        **kwargs,
    ):

        super().__init__(*args, persistor_id, **kwargs)

    @abstractmethod
    def run(self):
        raise NotImplementedError

    def send_model_and_wait(
        self,
        task_name: str = "train",
        data: FLModel = None,
        targets: Union[List[str], None] = None,
        min_responses: int = None,
        timeout: int = 0,
    ) -> List[FLModel]:

        return super().broadcast_model(
            task_name=task_name,
            data=data,
            targets=targets,
            min_responses=min_responses,
            timeout=timeout,
        )

    def send_model(
        self,
        task_name: str = "train",
        data: FLModel = None,
        targets: Union[List[str], None] = None,
        min_responses: int = None,
        timeout: int = 0,
        callback: Callable[[FLModel], None] = None,
    ) -> None:

        super().broadcast_model(
            task_name=task_name,
            data=data,
            targets=targets,
            min_responses=min_responses,
            timeout=timeout,
            blocking=False,
            callback=callback,
        )

    def load_model(self) -> FLModel:
        return super().load_model()

    def save_model(self, model: FLModel) -> None:
        super().save_model(model)

    def sample_clients(self, client_lists) -> List[str]:
        return super().sample_clients(client_lists)

class nt_FedAvg(nt_Model_Control_Pack):
    def __init__(self, *args, num_clients: int = 3,client_lists: list = None, num_rounds: int = 5,start_round: int = 0, initial_model : nn.Module, **kwargs,):

        super().__init__(*args, **kwargs)

        self.num_clients = num_clients
        self.num_rounds = num_rounds
        self.start_round = start_round
        self.client_lists = client_lists
        self.initial_model = initial_model

        self.current_round = None

    @staticmethod
    def _check_results(results: List[FLModel]):
        empty_clients = []
        for _result in results:
            if not _result.params:
                empty_clients.append(_result.meta.get("client_name", AppConstants.CLIENT_UNKNOWN))

        if len(empty_clients) > 0:
            raise ValueError(f"Result from client(s) {empty_clients} is empty!")

    @staticmethod
    def aggregate_fn(results: List[FLModel]) -> FLModel:
        if not results:
            raise ValueError("received empty results for aggregation.")

        aggr_helper = WeightedAggregationHelper()
        aggr_metrics_helper = WeightedAggregationHelper()
        all_metrics = True
        for _result in results:
            aggr_helper.add(
                data=_result.params,
                weight=_result.meta.get(FLMetaKey.NUM_STEPS_CURRENT_ROUND, 1.0),
                contributor_name=_result.meta.get("client_name", AppConstants.CLIENT_UNKNOWN),
                contribution_round=_result.current_round,
            )
            if not _result.metrics:
                all_metrics = False
            if all_metrics:
                aggr_metrics_helper.add(
                    data=_result.metrics,
                    weight=_result.meta.get(FLMetaKey.NUM_STEPS_CURRENT_ROUND, 1.0),
                    contributor_name=_result.meta.get("client_name", AppConstants.CLIENT_UNKNOWN),
                    contribution_round=_result.current_round,
                )

        aggr_params = aggr_helper.get_result()
        aggr_metrics = aggr_metrics_helper.get_result() if all_metrics else None

        aggr_result = FLModel(
            params=aggr_params,
            params_type=results[0].params_type,
            metrics=aggr_metrics,
            meta={"nr_aggregated": len(results), "current_round": results[0].current_round},
        )
        return aggr_result

    def aggregate(self, results: List[FLModel], aggregate_fn=None) -> FLModel:

        self.debug("Start aggregation.")
        self.event(AppEventType.BEFORE_AGGREGATION)
        self._check_results(results)

        if not aggregate_fn:
            aggregate_fn = self.aggregate_fn

        self.info(f"aggregating {len(results)} update(s) at round {self.current_round}")
        try:
            aggr_result = aggregate_fn(results)
        except Exception as e:
            error_msg = f"Exception in aggregate call: {secure_format_exception(e)}"
            self.exception(error_msg)
            self.panic(error_msg)
            return FLModel()
        self._results = []

        self.fl_ctx.set_prop(AppConstants.AGGREGATION_RESULT, aggr_result, private=True, sticky=False)
        self.event(AppEventType.AFTER_AGGREGATION)
        self.debug("End aggregation.")

        return aggr_result

    def update_model(self, model, aggr_result):

        self.event(AppEventType.BEFORE_SHAREABLE_TO_LEARNABLE)

        model = FLModelUtils.update_model(model, aggr_result)

        # persistor uses Learnable format to save model
        ml = make_model_learnable(weights=model.params, meta_props=model.meta)
        self.fl_ctx.set_prop(AppConstants.GLOBAL_MODEL, ml, private=True, sticky=True)

        self.event(AppEventType.AFTER_SHAREABLE_TO_LEARNABLE)

        return model


#############################################  FL Method ##########################################
# Basic Federated Learning (FedAVG)
from client_contribution.individual import nt_contrib_individual
from client_contribution.loo import nt_contrib_loo

class nt_FedAvg_Pack(nt_FedAvg):

    def run(self) -> None:
        self.info("Start FedAvg.")

        model = self.load_model()
        model.start_round = self.start_round
        model.total_rounds = self.num_rounds

        initial_model = self.initial_model

        '''이 부분은 이후 삭제할 예정'''



        DATASET_PATH = "/tmp/nvflare/data"
        transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
        batch_size = 256

        testset = torchvision.datasets.CIFAR10(root=DATASET_PATH, train=False, download=True, transform=transform)
        testloader = torch.utils.data.DataLoader(testset, batch_size=batch_size, shuffle=False, num_workers=2)
        
        
        DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
        
        #check FedAVG sample_client_num == client_list's length
        if self.num_clients != len(self.client_lists):
            self.info("Error : The number of clients does not match the length of the client list.")

        for self.current_round in range(self.start_round, self.start_round + self.num_rounds):
            self.info(f"Round {self.current_round} started.")
            model.current_round = self.current_round
            # Training client all-all
            clients = self.sample_clients(self.client_lists)

            results = self.send_model_and_wait(targets=clients, data=model)
            print('\n\n\n\n\n\n\n here : ',results)
            nt_contrib_individual(results, mode='norm')
            nt_contrib_loo(initial_model, results, DEVICE, testloader, 'basic')
            
            aggregate_results = self.aggregate(results, aggregate_fn=self.aggregate_fn)  
            model = self.update_model(model, aggregate_results)

            self.save_model(model)

        self.info("Finished FedAvg.")

class nt_FedAvg_Contrib_(nt_FedAvg):

    def run(self) -> None:
        self.info("Start FedAvg.")

        model = self.load_model()
        model.start_round = self.start_round
        model.total_rounds = self.num_rounds
        #check FedAVG sample_client_num == client_list's length
        if self.num_clients != len(self.client_lists):
            self.info("Error : The number of clients does not match the length of the client list.")

        for self.current_round in range(self.start_round, self.start_round + self.num_rounds):
            self.info(f"Round {self.current_round} started.")
            model.current_round = self.current_round
            # Training client all-all
            clients = self.sample_clients(self.client_lists)

            results = self.send_model_and_wait(targets=clients, data=model)

            aggregate_results = self.aggregate(results, aggregate_fn=self.aggregate_fn)  
            model = self.update_model(model, aggregate_results)

            self.save_model(model)

        self.info("Finished FedAvg.")



class nt_Fed_JOB(FedJob):
    def __init__(
        self,
        initial_model: nn.Module = None,
        name: str = "fed_job",
        min_clients: int = 1,
        mandatory_clients: Optional[List[str]] = None,
        key_metric: str = "accuracy",
        validation_json_generator: Optional[ValidationJsonGenerator] = None,
        intime_model_selector: Optional[IntimeModelSelector] = None,
        convert_to_fed_event: Optional[ConvertToFedEvent] = None,
        analytics_receiver: Optional[AnalyticsReceiver] = None,
        model_persistor: Optional[ModelPersistor] = None,
        model_locator: Optional[ModelLocator] = None,
    ):

        super().__init__(
            name=name,
            min_clients=min_clients,
            mandatory_clients=mandatory_clients,
        )

        self.initial_model = initial_model
        self.comp_ids = {}

        if validation_json_generator:
            validate_object_for_job("validation_json_generator", validation_json_generator, ValidationJsonGenerator)
        else:
            validation_json_generator = ValidationJsonGenerator()
        self.to_server(id="json_generator", obj=validation_json_generator)

        if intime_model_selector:
            validate_object_for_job("intime_model_selector", intime_model_selector, IntimeModelSelector)
            self.to_server(id="model_selector", obj=intime_model_selector)
        elif key_metric:
            self.to_server(id="model_selector", obj=IntimeModelSelector(key_metric=key_metric))

        if convert_to_fed_event:
            validate_object_for_job("convert_to_fed_event", convert_to_fed_event, ConvertToFedEvent)
        else:
            convert_to_fed_event = ConvertToFedEvent(events_to_convert=[ANALYTIC_EVENT_TYPE])
        self.convert_to_fed_event = convert_to_fed_event

        if analytics_receiver:
            validate_object_for_job("analytics_receiver", analytics_receiver, AnalyticsReceiver)
        else:
            analytics_receiver = TBAnalyticsReceiver()

        self.to_server(
            id="receiver",
            obj=analytics_receiver,
        )

        if initial_model:
            self.comp_ids.update(
                self.to_server(PTModel(model=initial_model, persistor=model_persistor, locator=model_locator))
            )

    def set_up_client(self, target: str):
        self.to(id="event_to_fed", obj=self.convert_to_fed_event, target=target)


class nt_Job_controller(BaseFedJob):
    def __init__(
        self,
        initial_model: nn.Module,
        n_clients: int,
        num_rounds: int,
        client_lists: list = None,
        name: str = "fed_job",
        min_clients: int = 1,
        mandatory_clients: Optional[List[str]] = None,
        key_metric: str = "accuracy",
        FL_method: str = "FedAvg",
    ):

        if not isinstance(initial_model, nn.Module):
            raise ValueError(f"Expected initial model to be nn.Module, but got type f{type(initial_model)}.")
        
        if client_lists == None:
            client_lists = [idx for idx in range(n_clients)]

        super().__init__(initial_model, name, min_clients, mandatory_clients, key_metric)
        if FL_method == "FedAvg":
            controller = nt_FedAvg_Pack(num_clients=n_clients, client_lists = client_lists, num_rounds=num_rounds,persistor_id=self.comp_ids["persistor_id"],initial_model=initial_model)
        self.to_server(controller)