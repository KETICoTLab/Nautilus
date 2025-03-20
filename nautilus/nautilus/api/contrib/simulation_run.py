import sys
from pathlib import Path
# sys.path에 추가되는 경로 확인
current_path = str(Path(__file__).resolve().parent.parent.parent)
from util.job_tools import nt_Job_controller
from nvflare.job_config.script_runner import ScriptRunner
from client_test import SimpleNetwork

# 현재 파일의 절대 경로를 기준으로 workspace/jobs 경로 설정
BASE_DIR = Path(__file__).resolve().parent
EXPORT_PATH = BASE_DIR / "../../workspace/jobs"

if __name__ == "__main__":
    n_clients = 2
    num_rounds = 2
    train_script = "client_contribution/src/hello-pt_cifar10_fl.py"

    # Client Selection Function is Now here
    
    job = nt_Job_controller(
        name="hello-pt_cifar10_fedavg", n_clients=n_clients, num_rounds=num_rounds, initial_model=SimpleNetwork()
    )

    # Add clients
    for i in range(n_clients):
        executor = ScriptRunner(
            script=train_script, script_args=""  # f"--batch_size 32 --data_path /tmp/data/site-{i}"
        )
        job.to(executor, f"site-{i}")

    print(f"export_job > str(EXPORT_PATH.resolve()): {str(EXPORT_PATH.resolve())}")
    job.simulator_run(str(EXPORT_PATH.resolve()))
