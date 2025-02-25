import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import argparse
import json
from nvflare.app_opt.pt.job_config.fed_avg import FedAvgJob
from nvflare.job_config.script_runner import ScriptRunner

# CLI 인자 처리
parser = argparse.ArgumentParser(description="Train a federated model with FLARE")
parser.add_argument("--n_clients", type=int, required=True, help="n_clients")
parser.add_argument("--num_rounds", type=int, required=True, help="num_rounds")
parser.add_argument("--train_script", type=str, required=True, help="src/train.py")
parser.add_argument("--job_id", type=str, required=True, help="job_id")
args = parser.parse_args()

# 현재 파일이 위치한 디렉토리 찾기 (현재 위치: /home/cotlab/workspace/nautilus/nautilus/simulation)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))  # 두 단계 위로 이동하여 /home/cotlab/workspace/nautilus 찾기
export_job_loc = os.path.join(BASE_DIR, "workspace", "jobs")  # 상대경로 설정
train_script = os.path.join(BASE_DIR, "nautilus", "simulation", "src", args.train_script)
# 서버 설정
n_clients = args.n_clients
num_rounds = args.num_rounds
job_id = args.job_id

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
    job = FedAvgJob(
        name=job_id, n_clients=n_clients, num_rounds=num_rounds, initial_model=SimpleNetwork()
    )

    # Add clients
    for i in range(n_clients):
        executor = ScriptRunner(
            script=train_script, script_args=""  # f"--batch_size 32 --data_path /tmp/data/site-{i}"
        )
        job.to(executor, f"site-{i + 1}")

    job.export_job(export_job_loc)
            
# python fedavg_create_job_runner.py --n_clients 3 --num_rounds 1 --train_script src/hello-pt_cifar10_network.py --job_id test-job
