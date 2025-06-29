import os
import subprocess
import sys
# 현재 파일 기준으로 최상위 Nautilus 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# 같은 디렉토리(`core/communicate/`)에 있는 모듈 import
from .k8s import (
    is_exist_namespace,
    create_namespace,
    create_client_deployment,
    create_server_deployment,
    copy_to_container,
    connect_get_namespaced_pod_exec
)
from .containerd import is_image_exists, remove_containerd_image, load_containerd_image
from .minio_storage import pull_pv_image_tar_from_minio

    # 0. minio 에 이미지 불러오기
    # 1. Deployment
    #  - namepsace 조회 
    #  - nvflare namespace 없으면 생성
    #  - nvflare namespace 에 client deployment 실행
    # 2. train.py 파일 컨테이너로 복사
    # 3. simulation exec 명령어 날리기
def run_join_playbook(target_host, data_provider_id, master_node_ip):
  print(f"validation.py - run_join_playbook) target host: {target_host}")
  script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../workspace/scripts/join_worker_node.sh"))

  # ✅ `subprocess.Popen`을 사용하여 실시간 로그 출력
  command = ["bash", script_path, target_host, data_provider_id, master_node_ip]
  process = subprocess.Popen(
      command,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      text=True,
      bufsize=1,  # 실시간 출력
      universal_newlines=True
  )
  print(f"validation.py - run_join_playbook) command: {command}")
  # ✅ 표준 출력(STDOUT) 실시간 출력
  for line in iter(process.stdout.readline, ""):
      print("Playbook STDOUT:", line.strip())

  # ✅ 표준 에러(STDERR) 실시간 출력
  for line in iter(process.stderr.readline, ""):
      print("Playbook STDERR:", line.strip())

  # ✅ 프로세스 종료 대기
  process.stdout.close()
  process.stderr.close()
  process.wait()
  
  print(f"validation.py - run_join_playbook) Playbook execution finished with exit code {process.returncode}")

def run_ansible_playbook(target_host):
    """
    Ansible Playbook 실행 함수.
    - target_host가 'localhost'이면 로컬 모드로 실행하며 local_tar_path 인자를 포함
    - 그 외에는 vault 및 extra_vars 방식으로 실행
    """

    if target_host == "localhost":
        # host_vars/localhost.yml 파일 경로
        extra_vars_file = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "../../workspace/ansible_project/inventory/host_vars/localhost.yml"
        ))

        playbook_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../workspace/ansible_project/playbook/load_nautilus_img_master.yml"))
        command = [
            "ansible-playbook",
            "-i", "localhost,",
            "-e", "target_host=localhost",
            "--extra-vars", f"@{extra_vars_file}",
            playbook_path
        ]

    else:
        # 일반 worker 대상 실행 (Vault 포함)
        vault_password_file = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "../../workspace/ansible_project/inventory/host_vars/vaultpass"
        ))
        extra_vars_file = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            f"../../workspace/ansible_project/inventory/host_vars/{target_host}.yml"
        ))

        print(f"validation.py - run_ansible_playbook) target host: {target_host}")
        playbook_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../workspace/ansible_project/playbook/load_nautilus_img.yml"))
        print(f"validation.py - run_ansible_playbook) playbook_path: {playbook_path}")
        
        command = [
            "ansible-playbook",
            "-i", f"{target_host},",
            "-e", f"target_host={target_host}",
            "--vault-password-file", vault_password_file,
            "--extra-vars", f"@{extra_vars_file}",
            playbook_path
        ]

    print(f"[INFO] Ansible command to run: {' '.join(command)}")

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    for line in iter(process.stdout.readline, ""):
        print("Playbook STDOUT:", line.strip())

    for line in iter(process.stderr.readline, ""):
        print("Playbook STDERR:", line.strip())

    process.stdout.close()
    process.stderr.close()
    process.wait()
    print(f"validation.py - run_ansible_playbook) load_nautilus_img execution finished with exit code {process.returncode}")


def apply_nautilus_deployment(project_id: str, site: int, node_name: str, who: str):
    print(f"apply_nautilus_deployment ing..")
    namespace = "nautilus"
    if not is_exist_namespace(namespace):
        create_namespace(namespace)

    if who == "client":
        print(f"create_client_deployment ing..")
        create_client_deployment(project_id, site, node_name, use_gpu=False)
    elif who == "server":
        print(f"create_server_deployment ing..")
        create_server_deployment(project_id, node_name, use_gpu=False)
    else:
        raise ValueError("Invalid value for 'who'. Must be either 'client' or 'server'.")
          
          
## node name: data_provider_id
## pod name : {project_ID}-client-site-N 이런식으로~
## train.py -> ui에서 선택한 파일이다 보니, 로컬 파일이 아니라서 ui에서 받은 파일을 어떻게 이 함수로 넘길지는 생각해 봐야 함
### => 로컬에 저장. {project_id}_train.py 이런식으로
### /workspace/nautilus/nautilus/simulation/src 위치에 train.py 파일 전송
def copy_local_to_container(pod_name: str, local_file_path: str, container_path: str, namespace: str = "nautilus", type: str = "file"):
  print(f"copy_local_to_container: namespace: {namespace}, pod_name: {pod_name}, local_file_path: {local_file_path}, container_path: {container_path}, type: {type}")
  copy_to_container(pod_name, namespace, local_file_path, container_path, type)

### /workspace/nautilus/nautilus/simulation/fedavg_script_runner_pt.py 실행
def execute_command(pod_name: str, command: str, namespace: str = "nautilus"):
  # pod_name = "" 
  # command = "" # simulation 실행 / job 실행 등 command 넣으면 됨
  print(f"execute_command: namespace: {namespace}, pod_name: {pod_name}, command: {command}")
  output = connect_get_namespaced_pod_exec(namespace, pod_name, command)
  print("[Pod Output]:", output)
     
#run_ansible_playbook()
