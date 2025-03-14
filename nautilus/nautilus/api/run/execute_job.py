import os  
import json
import argparse
import subprocess
import sys
from pathlib import Path 
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from util.job_tools import nt_Job_controller
from nvflare.job_config.script_runner import ScriptRunner
from client_test import SimpleNetwork
from core.communicate.validation import (
    execute_command
)

def main(project_id, job_id):
    namespace = "nautilus-pv-updated"
    pod_name = f"{project_id}-server"
    
    # 실행할 명령어 정의
    admin_startup_command = f"/workspace/nautilus/nautilus/workspace/provision/{project_id}/prod_00/admin@nvidia.com/startup/start.sh"
    user_name_command = "admin@nvidia.com"
    submit_job_command = f"/workspace/nautilus/nautilus/workspace/jobs/{job_id}"

    print(f"Starting job execution on server: {pod_name}")

    # 1. 관리자 Start-up 실행
    print(f"- Executing (admin_startup_command): {admin_startup_command}")
    execute_command(pod_name=pod_name, command=admin_startup_command, namespace=namespace)

    # 2. 사용자 이름 명령 실행
    print(f"- Executing (user_name_command): {user_name_command}")
    execute_command(pod_name=pod_name, command=user_name_command, namespace=namespace)

    # 3. Job 제출 명령 실행
    print(f"- Executing (submit_job_command): {submit_job_command}")
    execute_command(pod_name=pod_name, command=submit_job_command, namespace=namespace)

    print("Job execution completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy Nautilus Federated Learning Simulation")
    parser.add_argument("--project_id", type=str, required=True, help="project_id")
    parser.add_argument("--job_id", type=str, required=True, help="Job name") #hello-pt_cifar10_fedavg

    args = parser.parse_args()

    main(args.project_id, args.job_id)
