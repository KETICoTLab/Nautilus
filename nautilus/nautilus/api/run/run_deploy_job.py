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
from nautilus.core.communicate.k8s import (
    get_pod_name_by_deployment
)
def main(config_path, job_id):
    """Config 파일을 로드하여 Nautilus 배포 및 실행"""
    # Config 파일 로드
    config_full_path = os.path.join(ROOT_BASE_DIR, "nautilus", "workspace", "configs", config_path)
    with open(config_full_path, "r") as f:
        config_data = json.load(f)

    # Config 데이터 추출
    project_id = config_data["project_id"]
    client_info = config_data["client_info"]
    number_of_client = config_data["number_of_client"]
    HOST = config_data["HOST"]

    namespace = "nautilus-pv-updated"
    print(f"Starting deploy job for Project: {project_id}")
    
    server_pod_name = f"{project_id}-server"
    server_pod_full_name = get_pod_name_by_deployment(namespace, server_pod_name)
    print(f"Deploying Server | Pod: {server_pod_name} | pod_full_name: {server_pod_full_name}")    
    

    # server측 Job 폴더 배포
    job_id = "hello-pt_cifar10_fedavg"
    job_dir = os.path.join(BASE_DIR, "nautilus",  "workspace", "jobs", job_id)
    container_path = "/workspace/nautilus/nautilus/workspace/jobs"
    copy_local_to_container(
        pod_name=server_pod_full_name,
        local_file_path=job_dir,
        container_path=container_path,
        namespace=namespace,
        type="folder"
    )
    
    # client측 Job 폴더 배포
    for i in range(number_of_client):
        site = i + 1  # site-1, site-2, ... 순차 증가
        pod_name = f"{project_id}-site-{site}"
        pod_full_name = get_pod_name_by_deployment(namespace, pod_name)
        print(f"Deploying Site-{site} | Pod: {pod_name} | pod_full_name: {pod_full_name}")

        # job 폴더 복사
        print(f"Starting copy_local_to_container")
        copy_local_to_container(
            pod_name=pod_full_name,
            local_file_path=job_dir,
            container_path=container_path,
            namespace=namespace,
            type="folder"
        )

    print("All deployments completed successfully!")

if __name__ == "__main__":
    print("wellcome successfully!")
    parser = argparse.ArgumentParser(description="Deploy Nautilus Federated Learning Simulation")
    parser.add_argument("--config_path", type=str, required=True, help="Path to the configuration JSON file")
    parser.add_argument("--job_id", type=str, required=True, help="Job name")

    args = parser.parse_args()

    main(args.config_path, args.job_id)
