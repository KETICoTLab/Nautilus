# run_create_job
import os
import json
import argparse
import subprocess
import sys

# 📌 ROOT_BASE_DIR `nautilus` 루트 디렉토리로 설정
ROOT_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT_BASE_DIR)
from nautilus.core.communicate.validation import (
    copy_local_to_container,
    execute_command
)

create_job_py_path = os.path.join(ROOT_BASE_DIR, "nautilus", "simulation", "fedavg_create_job_runner.py")
print(f"create_job_py_path: {create_job_py_path}")
def main(config_path, job_id, aggr_function, num_global_iteration, num_local_epoch):
    """Config 파일을 로드하여 Nautilus 배포 및 실행"""
    
    config_full_path = os.path.join(ROOT_BASE_DIR, "nautilus", "workspace", "configs", config_path)
    with open(config_full_path, "r") as f:
        config_data = json.load(f)

    project_id = config_data["project_id"]
    client_info = config_data["client_info"]
    number_of_client = config_data["number_of_client"]
    HOST = config_data["HOST"]

    namespace = "nautilus-pv-updated"
    server_pod_name = f"{project_id}-server"
    server_startup_command = f"/workspace/nautilus/nautilus/workspace/provision/{project_id}/prod_00/mylocalhost/startup/start.sh"
    
    # 0. FedAvg Job 생성
    print(f"* Starting create job for Project: {project_id}")

    job_command = [
        "python", create_job_py_path,
        "--n_clients", str(number_of_client),
        "--num_rounds", str(num_global_iteration),
        "--train_script", "hello-pt_cifar10_network.py",
        "--job_id", job_id
    ]
    subprocess.run(job_command, check=True)
    print("Job creation completed!")

    # 1. 서버 시작 (대기 상태 진입)
    print(f"* Starting server: {server_pod_name}")
    execute_command(pod_name=server_pod_name, command=server_startup_command, namespace=namespace)

    # 2. 생성된 Job 폴더 배포
    job_dir = os.path.join(ROOT_BASE_DIR, "nautilus", "workspace", "jobs", job_id)

    for i in range(number_of_client):
        site = i + 1  # site-1, site-2, ... 순차 증가
        pod_name = f"{project_id}-site-{site}"
        train_py_path = os.path.join(ROOT_BASE_DIR, "nautilus", "simulation", "src", f"{project_id}_train.py")
        container_path = "/workspace/nautilus/workspace/jobs"
        client_startup_command = f"/workspace/nautilus/workspace/provisioning/{project_id}/prod_00/site-{site}/startup/start.sh"

        print(f"* Deploying Site-{site} | Pod: {pod_name}")

        # 2-1. job 폴더 복사
        print(f"* Copying job folder to container...")
        copy_local_to_container(
            pod_name=pod_name,
            local_file_path=job_dir,
            container_path=container_path,
            namespace=namespace,
            type="folder"
        )

        # 2-2. client start-up 실행
        print(f"🏃 Executing client start-up command...")
        execute_command(pod_name=pod_name, command=client_startup_command, namespace=namespace)

    print("All deployments completed successfully!")

if __name__ == "__main__":
    print("🎉 Welcome! Running Nautilus Job Creation Process.")

    parser = argparse.ArgumentParser(description="Deploy Nautilus Federated Learning Simulation")
    parser.add_argument("--config_path", type=str, required=True, help="Path to the configuration JSON file")
    parser.add_argument("--job_id", type=str, required=True, help="Job ID")
    parser.add_argument("--aggr_function", type=str, required=True, help="Aggregation function")
    parser.add_argument("--num_global_iteration", type=int, required=True, help="Number of global iterations")
    parser.add_argument("--num_local_epoch", type=int, required=True, help="Number of local epochs")

    args = parser.parse_args()

    main(args.config_path, args.job_id, args.aggr_function, args.num_global_iteration, args.num_local_epoch)

