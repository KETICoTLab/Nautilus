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
    execute_command
)
from nautilus.core.communicate.k8s import (
    get_pod_name_by_deployment
)

def main(project_id, job_id):
    namespace = "nautilus-pv-updated"
    pod_name = f"{project_id}-server"
    job_id = "hello-pt_cifar10_fedavg"
    print(f"Starting execute job for Project: {project_id}")
    
    server_pod_name = f"{project_id}-server"
    server_pod_full_name = get_pod_name_by_deployment(namespace, server_pod_name)
    print(f"Deploying Server | Pod: {server_pod_name} | pod_full_name: {server_pod_full_name}")    
    
    # 실행할 명령어 정의
    admin_startup_command = f"/workspace/nautilus/nautilus/workspace/provisioning/{project_id}/prod_00/admin@nvidia.com/startup/start.sh"
    user_name_command = "admin@nvidia.com"
    submit_job_command = f"/workspace/nautilus/nautilus/workspace/jobs/{job_id}"

    print(f"Starting job execution on server: {server_pod_full_name}")

    # 1. 관리자 Start-up 실행
    print(f"- Executing (admin_startup_command): {admin_startup_command}")
    execute_command(pod_name=server_pod_full_name, command=admin_startup_command, namespace=namespace)

    # 2. 사용자 이름 명령 실행
    print(f"- Executing (user_name_command): {user_name_command}")
    execute_command(pod_name=server_pod_full_name, command=user_name_command, namespace=namespace)

    # 3. Job 제출 명령 실행
    print(f"- Executing (submit_job_command): {submit_job_command}")
    execute_command(pod_name=server_pod_full_name, command=submit_job_command, namespace=namespace)

    print("Job execution completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy Nautilus Federated Learning Simulation")
    parser.add_argument("--project_id", type=str, required=True, help="project_id")
    parser.add_argument("--job_id", type=str, required=True, help="Job name")

    args = parser.parse_args()

    main(args.project_id, args.job_id)
