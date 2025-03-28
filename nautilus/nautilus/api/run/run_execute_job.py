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
    pod_name = f"{project_id}-server"
    print(f"Starting execute job for Project: {project_id}")
    '''
    server_pod_name = f"{project_id}-server"
    server_pod_full_name = get_pod_name_by_deployment(deployment_name=server_pod_name)
    print(f"Deploying Server | Pod: {server_pod_name} | pod_full_name: {server_pod_full_name}")    
    '''
    # 실행할 명령어 정의
    # 에러날 시 cd로 진입 후에 ./fl_admin.sh 로 실행
    admin_startup_command = f"/workspace/nautilus/nautilus/workspace/provisioning/{project_id}/prod_00/admin@nvidia.com/startup/fl_admin.sh" 
    user_name_command = "admin@nvidia.com"
    submit_job_command = f"submit_job /workspace/nautilus/nautilus/workspace/jobs/{job_id}"
    submit_command = f"{admin_startup_command} && {user_name_command} && {submit_job_command}"

    print(f"Starting job execution on server: {submit_command}")
    
    print(f"- Executing (command): {submit_command}")
    '''
    execute_command(pod_name=server_pod_full_name, command=submit_command)
    '''
    execute_command(pod_name="mylocalhost", command=submit_command, namespace="default")

    print("Job execution completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy Nautilus Federated Learning Simulation")
    parser.add_argument("--project_id", type=str, required=True, help="project_id")
    parser.add_argument("--job_id", type=str, required=True, help="Job name")

    args = parser.parse_args()

    main(args.project_id, args.job_id)
