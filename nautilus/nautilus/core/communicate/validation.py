# from k8s import is_exist_namespace, create_namespace, create_client_deployment, copy_to_container
# from containerd import is_image_exists, remove_containerd_image, load_containerd_image
# from minio_storage import pull_pv_image_tar_from_minio
import os
import subprocess

    # 0. minio 에 이미지 불러오기
    # 1. Deployment
    #  - namepsace 조회 
    #  - nvflare namespace 없으면 생성
    #  - nvflare namespace 에 client deployment 실행
    # 2. train.py 파일 컨테이너로 복사
    # 3. simulation exec 명령어 날리기


def run_ansible_playbook(playbook_path, target_host):
  command = ["ansible-playbook", playbook_path, "--extra-vars", f"target_host={target_host}"]
  process = subprocess.run(command, capture_output=True, text=True)

  print("Playbook STDOUT:", process.stdout)
  print("Playbook STDERR:", process.stderr)

### playbook생성. 선택한 data에 맞는 client의 host를 조회하여 반복문으로 함수 실행 
def load_nautilus_image(target_host):
  playbook_path = "./load_nautilus_img.yml"
  run_ansible_playbook(playbook_path, target_host)


def apply_nautilus_deployment(project_id: str, site: int, node_name: str):
  namespace = "nautilus"
  if not is_exist_namespace(namespace):
    create_namespace(namespace)
  else:
    create_server_deployment(project_id, node_name)
    create_client_deployment(project_id, site, node_name)

## node name: data_provider_id
## pod name : {project_ID}-client-site-N 이런식으로~
## train.py -> ui에서 선택한 파일이다 보니, 로컬 파일이 아니라서 ui에서 받은 파일을 어떻게 이 함수로 넘길지는 생각해 봐야 함
### => 로컬에 저장. {project_id}_train.py 이런식으로
### /workspace/nautilus/nautilus/simulation/src 위치에 train.py 파일 전송
def copy_local_to_container(pod_name: str, local_file_path: str, container_path: str, namespace: str = "nautilus", type: str = "file"):
  print(f"copy_local_to_container: namespace: {namespace}, pod_name: {pod_name}, local_file_path: {local_file_path}, container_path: {container_path}, type: {type}")
  # copy_to_container(pod_name, namespace, local_file_path, container_path, type)

### /workspace/nautilus/nautilus/simulation/fedavg_script_runner_pt.py 실행
def execute_command(pod_name: str, command: str, namespace: str = "nautilus"):
  # pod_name = "" 
  # command = "" # simulation 실행 / job 실행 등 command 넣으면 됨
  print(f"execute_command: namespace: {namespace}, pod_name: {pod_name}, command: {command}")

  # connect_get_namespaced_pod_exec(namespace, pod_name, command)
     