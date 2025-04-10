import os
import sys
import socket
import docker
import argparse
from minio import Minio
from io import BytesIO
from pathlib import Path

# 현재 파일 기준으로 최상위 Nautilus 디렉토리를 sys.path에 추가
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# 올바른 import 경로
from util.auto_save.utils import (
    set_minio_client,
    download_from_minio,
    load_docker_image,
    get_docker_image_id,
    run_docker_container,
    copy_file_to_container,
    execute_script_in_container,
    commit_docker_container,
    write_config_to_json,
    generate_project_yaml,
    save_docker_image,
    upload_to_minio
    )



def deploy():
    """Execute the provision & deployment process."""
    MINIO_ENDPOINT = "http://localhost:9000"
    MINIO_BUCKET = "images"
    IMAGE_NAME = "nautilus-default-img.tar"
    TAR_IMAGE_NAME = "nautilus-vlight:0.4" #install verion 11G

    # 현재 provision.py의 위치를 기준으로 Nautilus/nautilus/nautilus/workspace/images/ 설정
    LOCAL_WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../workspace/images/"))
    
    CONTAINER_NAME = "nautilus-container"
    NEW_IMAGE_NAME = "nautilus-pv-updated:latest"
    NEW_IMAGE_TAR = "nautilus-pv-updated.tar"
    
    # 저장 경로 조정
    TAR_PATH = os.path.join(LOCAL_WORKSPACE, NEW_IMAGE_TAR)
    
    minio_client = set_minio_client()
    
    image_path = os.path.join(LOCAL_WORKSPACE, IMAGE_NAME)
    print(f"[PASS] download_from_minio) image_path: {image_path}")
    
    # image_path 에 scp로 옮겨놓았음
    #download_from_minio(minio_client, MINIO_BUCKET, IMAGE_NAME, image_path)
    
    docker_client = docker.from_env()
    load_docker_image(docker_client, image_path)
    image_id = get_docker_image_id(docker_client, TAR_IMAGE_NAME)
    container = run_docker_container(docker_client, CONTAINER_NAME, image_id)
    
    # 프로젝트 YML 파일 복사 경로 수정
    project_yml_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../workspace/provision/project.yml"))
    container_project_yml_path = "/workspace/nautilus/nautilus/api/etc/"
    
    copy_file_to_container(container, project_yml_path, container_project_yml_path)
    print(f"copy_file_to_container done...")

    # 컨테이너 내부에서 실행할 스크립트 경로 수정
    script_path = "/workspace/nautilus/nautilus/api/etc/nt_provision.py"
    
    execute_script_in_container(container, script_path)
    print(f"execute_script_in_container done...")
    
    commit_docker_container(docker_client, container, NEW_IMAGE_NAME)
    print(f"commit_docker_container done...")

    save_docker_image(NEW_IMAGE_NAME, TAR_PATH)
    print(f"save_docker_image done...")
    
    upload_to_minio(minio_client, MINIO_BUCKET, NEW_IMAGE_TAR, TAR_PATH)
    print(f"upload_to_minio done...")
    
    print(f"Deployment completed successfully. New image stored in MinIO: {MINIO_BUCKET}/{NEW_IMAGE_TAR}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Provisioning for Nautilus Federated Learning")
    parser.add_argument("--project_id", type=str, required=True, help="Project ID for provisioning")
    parser.add_argument("--project_name", type=str, required=True, help="Project Name")
    parser.add_argument("--number_of_client", type=int, required=True, help="Number of clients")

    args = parser.parse_args()

    config_data = {
        "project_id": args.project_id,
        "project_name": args.project_name,
        "number_of_client": args.number_of_client,
        "target_hosts": [],
        "client_info": {},
        "client_list": [],
        "nodes": []
    }
    
    # Save config as JSON
    write_config_to_json(config_data, config_data["project_id"])
    
    # Generate project.yml
    generate_project_yaml(config_data["project_id"])
    
    # Run deployment
    deploy()
