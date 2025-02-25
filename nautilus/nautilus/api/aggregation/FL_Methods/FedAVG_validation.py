# FedAVG_simulator.py
# FedAVG 알고리즘의 시뮬레이터 버전

from typing import List, Optional
import torch.nn as nn
from nvflare.app_common.workflows.fedavg import FedAvg
from nvflare.app_opt.pt.job_config.base_fed_job import BaseFedJob

class FedAvgSimulatorJob(BaseFedJob):
    def __init__(
        self,
        initial_model: nn.Module,
        n_clients: int,
        num_rounds: int,
        name: str = "fed_simulator_job",
        min_clients: int = 1,
        mandatory_clients: Optional[List[str]] = None,
        key_metric: str = "accuracy",
    ):

        if not isinstance(initial_model, nn.Module):
            raise ValueError(f"Expected initial model to be nn.Module, but got type {type(initial_model)}.")

        super().__init__(initial_model, name, min_clients, mandatory_clients, key_metric)

        controller = FedAvg(
            num_clients=n_clients,
            num_rounds=num_rounds,
            persistor_id=self.comp_ids["persistor_id"],
        )
        self.to_server(controller)

def create_FedAVG_simulator(n_client=1, num_rounds=5, initial_model=None):
    """
    FedAVG 시뮬레이터 연합학습을 실행하기 위한 함수.
    """
    if initial_model is None:
        raise ValueError("initial_model이 필요합니다.")
    
    return FedAvgSimulatorJob(initial_model, n_client, num_rounds)



