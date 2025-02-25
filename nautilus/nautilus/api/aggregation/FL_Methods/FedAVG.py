# FedAVG function
from typing import List, Optional

import torch.nn as nn
from nvflare.app_common.workflows.fedavg import FedAvg
from nvflare.app_opt.pt.job_config.base_fed_job import BaseFedJob

class FedAvgJob(BaseFedJob):
    def __init__(
        self,
        initial_model: nn.Module,
        n_clients: int,
        num_rounds: int,
        name: str = "fed_job",
        min_clients: int = 1,
        mandatory_clients: Optional[List[str]] = None,
        key_metric: str = "accuracy",
    ):

        if not isinstance(initial_model, nn.Module):
            raise ValueError(f"Expected initial model to be nn.Module, but got type f{type(initial_model)}.")

        super().__init__(initial_model, name, min_clients, mandatory_clients, key_metric)

        controller = FedAvg(
            num_clients=n_clients,
            num_rounds=num_rounds,
            persistor_id=self.comp_ids["persistor_id"],
        )
        self.to_server(controller)

def create_FedAVG(n_client = 1, num_rounds = 5, initial_model):
    return FedAvgJob(n_client, num_rounds, initial_model=initial_model)


