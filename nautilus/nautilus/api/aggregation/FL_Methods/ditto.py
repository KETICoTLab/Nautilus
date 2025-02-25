# ditto function 
import os
from abc import abstractmethod

import torch

from nvflare.apis.signal import Signal
from nvflare.app_opt.pt.fedproxloss import PTFedProxLoss

class PTDittoHelper(object):
    def __init__(
        self, criterion, model, optimizer, device, app_dir: str, ditto_lambda: float = 0.1, model_epochs: int = 1
    ):

        self.criterion = criterion
        self.model = model
        self.optimizer = optimizer
        if device is None:
            self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        else:
            self.device = device
        self.model_epochs = model_epochs
        
        self.prox_criterion = PTFedProxLoss(mu=ditto_lambda)
        
        if not isinstance(self.criterion, torch.nn.modules.loss._Loss):
            raise ValueError(f"criterion component must be torch loss. " f"But got: {type(self.criterion)}")
        if not isinstance(self.model, torch.nn.Module):
            raise ValueError(f"model component must be torch model. " f"But got: {type(self.model)}")
        if not isinstance(self.optimizer, torch.optim.Optimizer):
            raise ValueError(f"optimizer component must be torch optimizer. " f"But got: {type(self.optimizer)}")
        if not isinstance(self.device, torch.device):
            raise ValueError(f"device component must be torch device. " f"But got: {type(self.device)}")

        
        self.epoch_global = 0
        self.epoch_of_start_time = 0
        self.best_metric: int = 0
        self.model_file_path = os.path.join(app_dir, "personalized_model.pt")
        self.best_model_file_path = os.path.join(app_dir, "best_personalized_model.pt")

    def load_model(self, global_weights):
        if os.path.exists(self.model_file_path):
            model_data = torch.load(self.model_file_path)
            self.model.load_state_dict(model_data["model"])
            self.epoch_of_start_time = model_data["epoch"]
        else:
            self.model.load_state_dict(global_weights)
            self.epoch_of_start_time = 0
        if os.path.exists(self.best_model_file_path):
            model_data = torch.load(self.best_model_file_path)
            self.best_metric = model_data["best_metric"]

    def save_model(self, is_best=False):
        model_weights = self.model.state_dict()
        save_dict = {"model": model_weights, "epoch": self.epoch_global}
        if is_best:
            save_dict.update({"best_metric": self.best_metric})
            torch.save(save_dict, self.best_model_file_path)
        else:
            torch.save(save_dict, self.model_file_path)

    def update_metric_save_model(self, metric):
        self.save_model(is_best=False)
        if metric > self.best_metric:
            self.best_metric = metric
            self.save_model(is_best=True)

    @abstractmethod
    def local_train(self, train_loader, model_global, abort_signal: Signal, writer):
        raise NotImplementedError