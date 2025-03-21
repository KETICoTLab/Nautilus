import os
import sys
import json
import argparse
from pathlib import Path

# 현재 파일 기준으로 최상위 Nautilus 디렉토리를 sys.path에 추가
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from util.auto_save.utils import (
    download_from_minio,
    execute_script_in_container,
)
from core.communicate.validation import (
    load_nautilus_image,
    apply_nautilus_deployment,
    copy_local_to_container,
    execute_command
)
from core.communicate.k8s import (
    get_pod_name_by_deployment
)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def main(config_name):
    """Config 파일을 로드하여 Nautilus 배포 및 실행"""
    config_path = os.path.abspath(os.path.join(BASE_DIR, "../../workspace/configs", config_name))
    print(f"Load config: {config_path}")

    # Config 파일 로드
    with open(config_path, "r") as f:
        config_data = json.load(f)

    print(f"Load config_data: {config_data}")

    # Config 데이터 추출
    project_id = config_data["project_id"]
    target_hosts = config_data["target_hosts"]
    client_info = config_data["client_info"]
    number_of_client = config_data["number_of_client"]
    HOST = config_data["HOST"]
    nodes = config_data["nodes"]

    print(f"Starting Nautilus Deployment for Project: {project_id}")
    server_pod_name = f"{project_id}-server" 
    apply_nautilus_deployment(project_id=project_id, site=site, node_name="master-node", who="server")
    
    namespace = "nautilus"
    for i, target_host in enumerate(target_hosts):
        site = i + 1  # site-1, site-2, ... 순차 증가
        node_name = nodes[i] if i < len(nodes) else f"default-node-{site}"

        pod_name = f"{project_id}-site-{site}"
        train_py_path = os.path.abspath(os.path.join(BASE_DIR, "../../simulation/src/hello-pt_cifar10_network.py"))
        container_path = "/workspace/nautilus/nautilus/simulation/src"
                
        print(f"Deploying Site-{site} | Host: {target_host} | Node: {node_name} | Pod: {pod_name}")

        # 1. Nautilus Docker 이미지 로드
        load_nautilus_image(target_host)
        print(f"load_nautilus_image done..")

        # 2. Kubernetes 배포 실행
        apply_nautilus_deployment(project_id=project_id, site=site, node_name=node_name, who="client")
        print(f"apply_nautilus_deployment done..")

        print(f"pod_full_name searching for clients")
        pod_full_name = get_pod_name_by_deployment(namespace, pod_name)
        print(f"pod_full_name: {pod_full_name}")
        # 3. Train 파일 컨테이너에 복사
        copy_local_to_container(pod_name=pod_full_name, local_file_path=train_py_path, container_path=container_path, namespace=namespace)
        print(f"copy_local_to_container done..")
        
    # 4. simulation 실행 - pass?

    print(f"pod_full_name searching for server")
    server_pod_full_name = get_pod_name_by_deployment(namespace, server_pod_name)
    command = "python3 /workspace/nautilus/nautilus/api/contrib/simulation_run.py"
    execute_command(pod_name=server_pod_full_name, command=command, namespace=namespace)

    print("All deployments completed successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy Nautilus Federated Learning Simulation")
    parser.add_argument("--config", type=str, required=True, help="Path to the configuration JSON file")

    args = parser.parse_args()

    main(args.config)

"""
* 실행명령어
python validation_deploy.py --config ../../workspace/configs/provision-test_config.json
"""
