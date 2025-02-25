"""
provision.py

Nautilus 플랫폼에서 마스터 노드에서 실행되어 연합 학습(Federated Learning) 환경을 구축하고 프로비저닝(provisioning)을 수행함.  
주요 기능은 다음과 같음:

0. config파일을 통해 provision을 위한 project.yml 생성
1. MinIO에서 학습 환경을 위한 Docker 기본 이미지 다운로드
2. 다운로드한 Docker 이미지를 로컬 환경에 로드
3. 컨테이너 실행 후 project.yml 파일을 컨테이너 내부로 복사
4. 프로비저닝 스크립트 실행 및 학습 환경 설정
5. 변경된 컨테이너를 새로운 Docker 이미지로 커밋
6. 생성된 새로운 Docker 이미지를 MinIO에 업로드하여 저장

이 과정을 통해 Nautilus 플랫폼의 연합 학습 인프라를 자동으로 설정하고, 학습을 수행할 수 있도록 준비.
"""

import os
import docker
import argparse
from minio import Minio
from io import BytesIO
from nautilus.util.auto_save.utils import (
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
    MINIO_ENDPOINT = "http://10.252.73.35:9000"
    MINIO_BUCKET = "images"
    IMAGE_NAME = "nautilus-default-img.tar"
    LOCAL_WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    CONTAINER_NAME = "nautilus-container"
    NEW_IMAGE_NAME = "nautilus-pv-updated"
    NEW_IMAGE_TAR = "nautilus-pv-updated.tar"
    TAR_PATH = os.path.join(os.path.dirname(__file__), "workspace/images/" + NEW_IMAGE_TAR)
    minio_client = set_minio_client()
    
    image_path = os.path.join(LOCAL_WORKSPACE, IMAGE_NAME)
    download_from_minio(minio_client, MINIO_BUCKET, IMAGE_NAME, image_path)
    
    docker_client = docker.from_env()
    load_docker_image(docker_client, image_path)
    image_id = get_docker_image_id(docker_client, "nautilus-default-img:latest")
    container = run_docker_container(docker_client, CONTAINER_NAME, image_id)
    
    copy_file_to_container(container, os.path.join(LOCAL_WORKSPACE, "provisioning/project.yml"), "/workspace/nautilus/workspace/provisioning/")
    execute_script_in_container(container, "/workspace/nautilus/nautilus/api/etc/provision.py")
    commit_docker_container(docker_client, container, NEW_IMAGE_NAME)

    save_docker_image(NEW_IMAGE_NAME, TAR_PATH)
    upload_to_minio(minio_client, MINIO_BUCKET, NEW_IMAGE_TAR, TAR_PATH)
    
    print(f"Deployment completed successfully. New image stored in MinIO: {MINIO_BUCKET}/{NEW_IMAGE_TAR}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Provisioning for Nautilus Federated Learning")
    parser.add_argument("--project_id", type=str, required=True, help="Project ID for provisioning")
    parser.add_argument("--project_name", type=str, required=True, help="Project Name")
    parser.add_argument("--number_of_client", type=int, required=True, help="Number of clients")

    args = parser.parse_args()

    # "HOST": client측에서 post전송을 위한 정보
    config_data = {
        "project_id": args.project_id,
        "project_name": args.project_name,
        "number_of_client": args.number_of_client,
        "target_hosts":[],
        "client_info":{},
        "HOST" = "http://10.252.73.241:8000"
    }
    
    # Save config as JSON
    write_config_to_json(config_data, config_data["project_id"])
    
    # Generate project.yml
    generate_project_yaml(config_data["project_id"])
    
    # Run deployment
    deploy()
