# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import torch
import torch.nn as nn
import torch.nn.functional as F
import argparse
import requests
import json
from nvflare.app_opt.pt.job_config.fed_avg import FedAvgJob
from nvflare.job_config.script_runner import ScriptRunner

# CLI 인자 처리
parser = argparse.ArgumentParser(description="Train a federated model with FLARE")
parser.add_argument("--host", type=str, required=True, help="Server host URL (e.g., http://127.0.0.1:8000)")
parser.add_argument("--project_id", type=str, required=True, help="Project ID")
parser.add_argument("--client_id", type=str, required=True, help="Client ID")
args = parser.parse_args()

# 서버 설정
HOST = args.host
PROJECT_ID = args.project_id
CLIENT_ID = args.client_id
STATUS_URL = f"{HOST}/nautilus/v1/projects/{PROJECT_ID}/clients/{CLIENT_ID}/check_status"

class SimpleNetwork(nn.Module):
    def __init__(self):
        super(SimpleNetwork, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = torch.flatten(x, 1)  # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


if __name__ == "__main__":
    n_clients = 1
    num_rounds = 1
    train_script = "src/hello-pt_cifar10_network.py"

    job = FedAvgJob(
        name="hello-pt_cifar10_fedavg", n_clients=n_clients, num_rounds=num_rounds, initial_model=SimpleNetwork()
    )

    # Add clients
    for i in range(n_clients):
        executor = ScriptRunner(
            script=train_script, script_args=""  # f"--batch_size 32 --data_path /tmp/data/site-{i}"
        )
        job.to(executor, f"site-{i + 1}")

    try:
        job.simulator_run("/tmp/nvflare/jobs/workdir", gpu="0")
        print("Simulation completed successfully.")

        # 상태 전송
        payload = {"validation_status": 1}
        headers = {"Content-Type": "application/json"}

        response = requests.post(STATUS_URL, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            print(f"Status updated successfully: {response.json()}")
        else:
            print(f"Failed to update status: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Simulation failed with error: {e}")

        # 실패 상태 전송
        payload = {"validation_status": 0}
        try:
            response = requests.post(STATUS_URL, data=json.dumps(payload), headers=headers)
            print(f"Failure status updated: {response.status_code}, {response.text}")
        except Exception as post_error:
            print(f"Failed to send failure status: {post_error}")
            
# python fedavg_script_runner_pt.py --host "http://10.252.73.241:8000" --project_id "P-KR-test-pr2" --client_id "C-KR-cl-test3"