import yaml
import json
from typing import Any
import subprocess
import os
import docker
from minio import Minio
from io import BytesIO
from tqdm import tqdm
import requests
from requests.exceptions import ReadTimeout

def read_json_file(file_name: str) -> Any:
    """파일명을 받아서 JSON 파일을 읽고 반환하는 함수"""
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error reading JSON file {file_name}: {e}")
        return None
    
def write_config_to_json(data: Any, file_name: str) -> None:
    """JSON 데이터를 받아서 지정된 파일명으로 저장하는 함수"""
    config_path = os.path.join(os.path.dirname(__file__), "../../workspace/configs", f"{file_name}_config.json")
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)  # 디렉토리 자동 생성
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Config successfully written to {config_path}")
    except Exception as e:
        print(f"Error writing config to JSON: {e}")


def read_yaml_file(file_path):
    """파일명을 받아서 yaml 파일을 읽고 반환하는 함수"""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def write_yaml_file(file_path, data):
    """데이터를 받아서 지정된 파일명으로 저장하는 함수"""
    with open(file_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        

def generate_project_yaml(project_id):
    """
    config 파일을 읽어서 project.yml을 생성하는 함수
    ** path를 상대경로로 지정해야할 필요가 있음.
    # config JSON data example
        config_data = {
            "project_id":"test",
            "project_name":"test",
            "global_iteration": 3,
            "number_of_client": 2, 
            "local_epoch": 3, 
            "aggregate_method": "fedavg",
            "client_train_file_location":"/workspace/pt/src/cifar10_fl.py"
        }
    """    
    config_path = os.path.join(os.path.dirname(__file__), "../../workspace/configs/"+ project_id +"_config.json")
    origin_yaml_path = os.path.join(os.path.dirname(__file__), "../../workspace/provision/origin-project.yml")
    output_yaml_path = os.path.join(os.path.dirname(__file__), "../../workspace/provision/project.yml")
    
    config = read_json_file(config_path)
    origin_yaml = read_yaml_file(origin_yaml_path)
    
    number_of_client = config.get("number_of_client", 0)
    project_id = config.get("project_id", "")
    
    # name 값 업데이트
    #origin_yaml["name"] = project_id
    
    # 기존 participants 리스트 복사
    new_participants = []
    for participant in origin_yaml["participants"]:
        if participant["type"] != "client":
            new_participants.append(participant)
    
    # 새로운 client 항목 추가
    for i in range(1, number_of_client + 1):
        new_participants.append({
            "name": f"site-{i}",
            "type": "client",
            "org": "nvidia"
        })
    
    # participants 업데이트
    origin_yaml["participants"] = new_participants
    
    # 새로운 YAML 파일 저장
    write_yaml_file(output_yaml_path, origin_yaml)
    print(f"{output_yaml_path} has been created successfully.")
    

def run_shell_script():
    """
    주어진 쉘 스크립트를 실행하는 함수
    script_path: 실행할 쉘 스크립트의 경로 
    """
    try:
        # utils.py가 위치한 디렉토리 기준으로 상대경로 설정
        script_path = os.path.join(os.path.dirname(__file__), "../../workspace/scripts/provision_img_deploy.sh")
        subprocess.run(["bash", script_path], check=True)
        print(f"{script_path} 실행 완료")
    except subprocess.CalledProcessError as e:
        print(f"스크립트 실행 중 오류 발생: {e}")


def set_minio_client(endpoint="http://localhost:9000", access_key="minio", secret_key="minio123"):
    """MinIO 클라이언트 초기화"""
    print("[INFO] MinIO 클라이언트 초기화 중...")
    return Minio(endpoint.replace("http://", ""), access_key=access_key, secret_key=secret_key, secure=False)

def download_from_minio(minio_client, bucket, object_name, local_path):
    """MinIO에서 파일 다운로드"""

    # 파일 크기 조회
    stat = minio_client.stat_object(bucket, object_name)
    total_size = stat.size

    # tqdm을 사용한 파일 다운로드 진행률 표시
    with tqdm(
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
        desc=object_name
    ) as progress_bar:
        with open(local_path, "wb") as file_data:
            response = minio_client.get_object(bucket, object_name)
            for data in response.stream(32 * 1024):  # 32KB 단위로 스트리밍 다운로드
                file_data.write(data)
                progress_bar.update(len(data))

    print(f"[INFO] MinIO에서 다운로드 완료: {object_name}")


def load_docker_image(client, image_path):
    """Docker 이미지 스트리밍 로드 (OOM 방지 + 프로그레스 바)"""
    print(f"[INFO] Docker 이미지 로드 시작: {image_path}")
    client = docker.DockerClient(base_url='unix://var/run/docker.sock', timeout=1200) # 15분 타임아웃 설정

    file_size = os.path.getsize(image_path)  # 파일 크기 가져오기

    with open(image_path, "rb") as image_tar, tqdm(
        total=file_size, unit="B", unit_scale=True, unit_divisor=1024, desc="Loading Docker Image"
    ) as progress_bar:
        
        def read_in_chunks(file_obj, chunk_size=1024 * 1024):  # 1MB 단위로 읽기
            while True:
                chunk = file_obj.read(chunk_size)
                if not chunk:
                    break
                progress_bar.update(len(chunk))
                yield chunk

        client.images.load(read_in_chunks(image_tar))  # 스트리밍 방식으로 Docker에 로드

    print(f"[INFO] Docker 이미지 로드 완료: {image_path}")
    
def get_docker_image_id(client, image_name):
    """Docker 이미지 ID 가져오기"""
    print(f"[INFO] Docker 이미지 ID 검색: {image_name}")
    images = client.images.list()
    print(f"[INFO] all Docker 이미지: {images}")
    for image in images:
        if image_name in image.tags:
            print(f"[INFO] Docker 이미지 ID 찾음: {image.id}")
            return image.id
    print(f"[WARNING] Docker 이미지 ID 찾을 수 없음: {image_name}")
    return None

def run_docker_container(client, container_name, image_id):
    """Run a Docker container."""
    print(f"[INFO] Starting Docker container: {container_name} starting image_id: {image_id}")
    container = client.containers.run(image_id, "/bin/bash", name=container_name, detach=True, tty=True)
    print(f"[INFO] Docker container started: {container_name}")
    return container

def copy_file_to_container(container, local_path, container_path):
    """Copy a file from the host to a Docker container."""
    print(f"[INFO] Copying file: {local_path} -> {container_path}")
    os.system(f"docker cp {local_path} {container.id}:{container_path}")
    print(f"[INFO] File copied: {local_path} -> {container_path}")

def execute_script_in_container(container, script_path):
    """컨테이너 내부에서 지정된 디렉토리에서 Python 스크립트 실행"""
    script_dir = "/workspace/nautilus/nautilus/api/etc"  # 실행할 디렉토리
    script_name = "nt_provision.py"  # 실행할 스크립트

    print(f"[INFO] Changing working directory to {script_dir} in container")
    
    command = f"cd {script_dir} && python3 {script_name}"
    print(f"[INFO] Executing script in container: {command}")

    exit_code, output = container.exec_run(
        cmd=["/bin/sh", "-c", command],  # 쉘 환경에서 실행
        privileged=True,  # 루트 권한 부여
        user="root",  # 루트 계정으로 실행
        tty=True,  # 터미널 환경 활성화
        workdir=script_dir  # 실행 디렉토리 설정
    )

    print(f"[INFO] Script execution completed: {script_path}")
    print(f"[INFO] Exit Code: {exit_code}")
    print(f"[INFO] Output: {output.decode()}")

    if exit_code != 0:
        raise Exception(f"[ERROR] Script execution failed inside container: {output.decode()}")


def commit_docker_container(client, container, new_image_name):
    """Commit changes in a container to a new Docker image."""
    print(f"[INFO] Committing Docker container: {new_image_name}")
    image = container.commit(repository=new_image_name)
    print(f"[INFO] Docker container committed: {new_image_name}")
    return image
###
def save_docker_image(image_name: str, output_path: str):
    """Docker 이미지를 tar 파일로 저장"""    
    print(f"Saving Docker image: {image_name} to {output_path}")
    
    try:
        subprocess.run(["docker", "save", "-o", output_path, image_name], check=True)
        print(f"Docker image saved command: docker save -o {output_path} {image_name}")
        print(f"Docker image saved successfully: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to save Docker image: {e}")


def upload_to_minio(minio_client, bucket_name, object_name, file_path):
    
    file_size = os.path.getsize(file_path)
    chunk_size = 10 * 1024 * 1024  # 10MB씩 업로드

    print(f"upload_to_minio: {minio_client}, bucket_name: {bucket_name}, object_name: {object_name}, file_path: {file_path}")

    with open(file_path, "rb") as file_data, tqdm(total=file_size, unit="B", unit_scale=True, desc=f"Uploading {object_name}") as pbar:
        minio_client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=file_data,  # ✅ `bytes`가 아니라 `file_data` 객체 자체를 전달
            length=file_size,
            content_type="application/octet-stream"
        )
        pbar.update(file_size)  # ✅ 업로드가 완료되었으므로 진행률 업데이트

    print(f"File uploaded successfully: {object_name}")
    
    
def http_post(url, payload):
    """
    결과 데이터를 지정된 URL로 POST 요청을 보냄.

    :param url: 데이터를 보낼 엔드포인트
    :param payload: 전송할 데이터 (dict)
    :return: 서버 응답 (Response 객체)
    """
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  # 오류 발생 시 예외 처리
        return response.json()  # JSON 응답 반환
    except requests.exceptions.RequestException as e:
        print(f"POST 요청 실패: {e}")
        return None