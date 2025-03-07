# scaffold function
import copy

import torch
from torch.optim import Optimizer

def get_lr_values(optimizer: Optimizer):

    return [group["lr"] for group in optimizer.state_dict()["param_groups"]]


class PTScaffoldHelper(object):

    def __init__(self):
        self.cnt = 0
        self.c_global = None
        self.c_local = None
        self.c_delta_para = None

    def init(self, model):
        self.c_global = copy.deepcopy(model)
        self.c_local = copy.deepcopy(model)

        c_init_para = model.state_dict()
        for k in c_init_para.keys():
            c_init_para[k] = torch.zeros_like(c_init_para[k])
        self.c_global.load_state_dict(c_init_para)
        self.c_local.load_state_dict(c_init_para)

    def get_params(self):
        self.cnt = 0
        c_global_para = self.c_global.state_dict()
        c_local_para = self.c_local.state_dict()
        return c_global_para, c_local_para

    def model_update(self, model, curr_lr, c_global_para, c_local_para):
        net_para = model.state_dict()
        for key in net_para:
            net_para[key] = net_para[key] - curr_lr * (c_global_para[key] - c_local_para[key])
        model.load_state_dict(net_para)

        self.cnt += 1

    def terms_update(self, model, curr_lr, c_global_para, c_local_para, model_global):

        c_new_para = self.c_local.state_dict()
        self.c_delta_para = copy.deepcopy(self.c_local.state_dict())
        global_model_para = model_global.state_dict()
        net_para = model.state_dict()
        for key in net_para:
            c_new_para[key] = (
                c_new_para[key] - c_global_para[key] + (global_model_para[key] - net_para[key]) / (self.cnt * curr_lr)
            )
            self.c_delta_para[key] = (c_new_para[key] - c_local_para[key]).cpu().numpy()
        self.c_local.load_state_dict(c_new_para)

    def load_global_controls(self, weights):
        self.c_global.load_state_dict(weights)

    def get_delta_controls(self):
        if self.c_delta_para is None:
            raise ValueError("c_delta_para hasn't been computed yet!")
        return self.c_delta_para