from kubernetes import client, config
from typing import Optional
import subprocess
import shlex
from kubernetes.stream import stream

# def get_kubernetes_nodes():
#     # Kubernetes 클라이언트 구성을 로드합니다 (로컬 kubeconfig 파일 사용)
#     config.load_kube_config()
    
#     # CoreV1 API 클라이언트를 생성합니다
#     v1 = client.CoreV1Api()
    
#     # 노드 목록 가져오기
#     print("Listing Kubernetes nodes:")
#     try:
#         nodes = v1.list_node()
#         print(nodes.items[0])
#         for node in nodes.items:
#             print(f"Node Name: {node.metadata.name}")
#             for address in node.status.addresses:
#                 print(f"  Type: {address.type}, Address: {address.address}")
#             print(f"  Node Status: {node.status.conditions[-1].type} - {node.status.conditions[-1].status}")
#             print("-" * 40)
#     except Exception as e:
#         print(f"An error occurred: {e}")

# if __name__ == "__main__":
#     get_kubernetes_nodes()



# Kubernetes 클러스터 설정 로드

try:
    config.load_kube_config()  # 로컬 K8s 클러스터 (kubectl 사용 가능 시)
except config.ConfigException:
    config.load_incluster_config()  # 클러스터 내부 실행 시

# API 클라이언트 초기화
v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()
batch_v1 = client.BatchV1Api()
storage_v1 = client.StorageV1Api()

# --- Kubernetes 리소스 조회 함수들 --- #
def node_has_gpu(node_name: str) -> bool:
    """
    해당 노드가 GPU(nvidia.com/gpu)를 보유하고 있는지 확인
    예제)
    use_gpu = node_has_gpu("w-kr-pr-test03")
    create_client_deployment(
        project_id="p-kr-prtest09",
        site=1,
        node_name="w-kr-pr-test03",
        use_gpu=use_gpu
    )
    """
    try:
        node = v1.read_node(name=node_name)
        allocatable = node.status.allocatable or {}
        gpu_count = allocatable.get("nvidia.com/gpu", "0")
        return int(gpu_count) > 0
    except Exception as e:
        print(f"⚠️ Failed to check GPU for node '{node_name}': {e}")
        return False

def list_daemon_set_for_all_namespace():
    """모든 네임스페이스에서 DaemonSet 목록 조회"""
    return apps_v1.list_daemon_set_for_all_namespaces()

def list_deployment_for_all_namespace():
    """모든 네임스페이스에서 Deployment 목록 조회"""
    return apps_v1.list_deployment_for_all_namespaces()

def list_namespaced_daemon_set(namespace: str):
    """특정 네임스페이스에서 DaemonSet 목록 조회"""
    return apps_v1.list_namespaced_daemon_set(namespace)

def list_namespaced_deployment(namespace: str):
    """특정 네임스페이스에서 Deployment 목록 조회"""
    return apps_v1.list_namespaced_deployment(namespace)

def list_namespaced_replica_set(namespace: str):
    """특정 네임스페이스에서 ReplicaSet 목록 조회"""
    return apps_v1.list_namespaced_replica_set(namespace)

def list_replica_set_for_all_namespaces():
    """모든 네임스페이스에서 ReplicaSet 목록 조회"""
    return apps_v1.list_replica_set_for_all_namespaces()

def list_stateful_set_for_all_namespaces():
    """모든 네임스페이스에서 StatefulSet 목록 조회"""
    return apps_v1.list_stateful_set_for_all_namespaces()

def list_cron_job_for_all_namespaces():
    """모든 네임스페이스에서 CronJob 목록 조회"""
    return batch_v1.list_cron_job_for_all_namespaces()

def list_job_for_all_namespaces():
    """모든 네임스페이스에서 Job 목록 조회"""
    return batch_v1.list_job_for_all_namespaces()

def list_namespaced_cron_job(namespace: str):
    """특정 네임스페이스에서 CronJob 목록 조회"""
    return batch_v1.list_namespaced_cron_job(namespace)

def list_namespaced_job(namespace: str):
    """특정 네임스페이스에서 Job 목록 조회"""
    return batch_v1.list_namespaced_job(namespace)

def list_persistent_volume():
    """모든 Persistent Volume 조회"""
    return v1.list_persistent_volume()

def list_persistent_volume_claim_for_all_namespaces():
    """모든 네임스페이스에서 Persistent Volume Claim 조회"""
    return v1.list_persistent_volume_claim_for_all_namespaces()

def list_namespaced_persistent_volume_claim(namespace: str):
    """특정 네임스페이스에서 Persistent Volume Claim 조회"""
    return v1.list_namespaced_persistent_volume_claim(namespace)

def list_node():
    """클러스터 내 모든 노드 조회"""
    return v1.list_node()

def custom_list_node():
    """클러스터 내 모든 노드의 필요한 정보만 반환"""
    nodes = v1.list_node()
    
    node_list = []
    
    for node in nodes.items:
        metadata = node.metadata
        status = node.status
        
        # 노드 이름
        node_name = metadata.name

        # 노드 역할(Role) 찾기
        labels = metadata.labels or {}
        role = "unknown"
        for key in labels:
            if key.startswith("node-role.kubernetes.io/"):
                role = key.split("/")[-1]
                break
        
        # CPU 및 메모리 정보
        capacity = status.capacity or {}
        cpu = capacity.get("cpu", "unknown")
        memory = capacity.get("memory", "unknown")

        # Internal IP 찾기
        addresses = status.addresses or []
        internal_ip = next((addr.address for addr in addresses if addr.type == "InternalIP"), "unknown")

        # 노드 상태 (Ready 여부)
        conditions = status.conditions or []
        ready_status = next((cond.status for cond in conditions if cond.type == "Ready"), "False")

        # 결과 저장
        node_list.append({
            "node_name": node_name,
            "cpu": cpu,
            "memory": memory,
            "ip": internal_ip,
            "ready": ready_status == "True"
        })

    return node_list

def list_pod_for_all_namespaces():
    """모든 네임스페이스에서 Pod 목록 조회"""
    return v1.list_pod_for_all_namespaces()

def list_namespaced_pod(namespace: str):
    """특정 네임스페이스에서 Pod 목록 조회"""
    return v1.list_namespaced_pod(namespace)

def get_pod_name_by_deployment(deployment_name: str, namespace: str = "nautilus"):
    """Deployment가 생성한 Pod의 이름을 가져오는 함수"""

    # 해당 Deployment의 Pod 목록 조회
    pod_list = v1.list_namespaced_pod(namespace=namespace, label_selector=f"app={namespace}")
    for pod in pod_list.items:
        print(f"for pod in pod_list.items: {pod.metadata.name}")
        if pod.metadata.name.startswith(deployment_name):
            print(f"\n\n[return] {deployment_name} pod.metadata.name: {pod.metadata.name}\n\n")
            return pod.metadata.name  # 가장 먼저 찾은 Pod 반환
    
    print(f"\n\n[Return] NONE\n\n")
    return None  # Pod를 찾지 못한 경우

def list_pods_by_deployment(deployment_name: str, namespace: str = "nautilus"):
    """Deployment가 생성한 모든 Pod의 이름을 가져오는 함수"""
    config.load_kube_config()  # 쿠버네티스 클러스터 설정 로드

    # 해당 Deployment의 Pod 목록 조회
    pod_list = v1.list_namespaced_pod(namespace=namespace, label_selector=f"app={deployment_name}")

    pod_names = [pod.metadata.name for pod in pod_list.items]

    return pod_names  # 모든 Pod 이름 리스트 반환

def list_service_for_all_namespace():
    """모든 네임스페이스에서 Service 목록 조회"""
    return v1.list_service_for_all_namespaces()

def list_namespaced_service(namespace: str):
    """특정 네임스페이스에서 Service 목록 조회"""
    return v1.list_namespaced_service(namespace)

def list_storage_class():
    """스토리지 클래스 조회"""
    return storage_v1.list_storage_class()

def list_volume_attachment():
    """볼륨 어태치먼트 조회"""
    return storage_v1.list_volume_attachment()

def list_namespace():
    return v1.list_namespace()

def is_exist_namespace(namespace: str) -> bool:
    """주어진 namespace가 쿠버네티스 클러스터에 존재하는지 확인하는 함수."""
    try:
        namespaces = v1.list_namespace()  # 모든 namespace 목록 조회
        
        # 주어진 namespace가 목록에 존재하는지 확인
        return any(ns.metadata.name == namespace for ns in namespaces.items)
    
    except client.exceptions.ApiException as e:
        print(f"❌ Kubernetes namespace 조회 실패: {e}")
        return False

# --- Kubernetes 리소스 생성 함수들 --- #
def create_namespace(name: str):
    """네임스페이스 생성"""
    body = client.V1Namespace(metadata=client.V1ObjectMeta(name=name))
    
    try:
        v1.create_namespace(body)
        print(f"✅ Complete namesapce creation '{name}'.")
    except client.ApiException as e:
        if e.status == 409:  # 네임스페이스가 이미 존재할 경우
            print(f"⚠️ Namespace '{name}' is already exist.")
        else:
            print(f"❌ Failed namespace creation \n {e}")

def create_deployment(namespace: str, name: str, image: str, replicas: int = 1, container_port: int = 80):
    """Deployment 생성"""
    deployment = client.V1Deployment(
        metadata=client.V1ObjectMeta(name=name),
        spec=client.V1DeploymentSpec(
            replicas=replicas,
            selector=client.V1LabelSelector(
                match_labels={"app": name}
            ),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": name}),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name=name,
                            image=image,
                            ports=[client.V1ContainerPort(container_port=container_port)]
                        )
                    ]
                )
            )
        )
    )
    try:
        apps_v1.create_namespaced_deployment(namespace=namespace, body=deployment)
        print(f"✅ Deployment '{name}' is created in namespace '{namespace}'.")
    except client.ApiException as e:
        print(f"❌ Deployment creation failed: {e}")

def create_client_deployment(project_id: str ,site: int, node_name: str, namespace: str = "nautilus", image: str = "nautilus-pv-updated:latest", replicas: int = 1, use_gpu: bool = True):
    """Client용 Deployment 생성 함수 (GPU 사용 여부 선택 가능)"""

    # 리소스 설정 분기
    limits = {
        "memory": "8Gi",
        "cpu": "4"
    }
    requests = {
        "memory": "4Gi",
        "cpu": "2"
    }

    if use_gpu:
        limits["nvidia.com/gpu"] = "1"
        requests["nvidia.com/gpu"] = "1"

    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(
            name=f"{project_id}-site-{site}",
            labels={"app": namespace}
        ),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector=client.V1LabelSelector(
                match_labels={"app": namespace}
            ),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels={"app": namespace}
                ),
                spec=client.V1PodSpec(
                    node_selector={"kubernetes.io/hostname": node_name},
                    containers=[
                        client.V1Container(
                            name=f"{project_id}-site-{site}",
                            image=image,
                            image_pull_policy="Never",
                            resources=client.V1ResourceRequirements(
                                limits=limits,
                                requests=requests
                            ),
                            args=[
                                "-u", "-m", "nvflare.private.fed.app.client.client_train",
                                "-m", f"/workspace/nvfl/{project_id}-site-{site}", "-s", "fed_client.json",
                                "--set", "secure_train=true", f"uid={project_id}-site-{site}",
                                "config_folder=config", "org=nvidia"
                            ],
                            command=["/bin/bash", "-c", f"pip install --upgrade nvflare==2.5.2 torch tensorboard torchvision && /workspace/nautilus/nautilus/workspace/provision/{project_id}/prod_00/site-{site}/startup/sub_start.sh"]
                        )
                    ]
                )
            )
        )
    )

    # Create the Deployment in the cluster
    api_instance = client.AppsV1Api()

    try:
        api_instance.create_namespaced_deployment(namespace=namespace, body=deployment)
        print("✅ Deployment created successfully!")
    except client.exceptions.ApiException as e:
        print(f"❌ Exception when creating deployment: {e}")

def create_server_deployment(project_id: str , node_name: str, namespace: str = "nautilus", image: str = "nautilus-pv-updated:latest", replicas: int = 1, use_gpu: bool = True):
    """Deployment 생성 (role 없이 node_name 기반으로 배포, GPU 사용 여부 선택 가능)"""

    # 리소스 설정 분기
    limits = {
        "memory": "8Gi",
        "cpu": "4"
    }
    requests = {
        "memory": "4Gi",
        "cpu": "2"
    }

    if use_gpu:
        limits["nvidia.com/gpu"] = "1"
        requests["nvidia.com/gpu"] = "1"
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(
            name=f"{project_id}-server",
            labels={"app": namespace}
        ),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector=client.V1LabelSelector(
                match_labels={"app": namespace}
            ),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels={"app": namespace}
                ),
                spec=client.V1PodSpec(
                    node_selector={"kubernetes.io/hostname": node_name}, 
                    containers=[
                        client.V1Container(
                            name=f"server",
                            image=image,
                            image_pull_policy="Never",
                            resources=client.V1ResourceRequirements(
                                limits=limits,
                                requests=requests
                            ),
                            args=[
                                "-u", "-m", "nvflare.private.fed.app.server.server_train",
                                "-m", f"/workspace/nvfl/{project_id}-server", "-s", "fed_server.json",
                                "--set", "secure_train=true", "config_folder=config", "org=nvidia"
                            ],
                            command=["/bin/bash", "-c", f"pip install --upgrade nvflare==2.5.2 torch tensorboard torchvision && /workspace/nautilus/nautilus/workspace/provision/{project_id}/prod_00/mylocalhost/startup/sub_start.sh"]
                        )
                    ]
                )
            )
        )
    )

    # Create the Deployment in the cluster
    api_instance = client.AppsV1Api()
    namespace = namespace  # Change if deploying to a different namespace

    try:
        api_instance.create_namespaced_deployment(namespace=namespace, body=deployment)
        print("Deployment created successfully!")
    except client.exceptions.ApiException as e:
        print(f"Exception when creating deployment: {e}")


# --- Kubernetes 실행 함수들 --- #
# def connect_get_namespaced_pod_exec(namespace: str, pod_name: str, command: str):
#     return stream(
#         v1.connect_get_namespaced_pod_exec,
#         name=pod_name,
#         namespace=namespace,
#         command=shlex.split(command),
#         stderr=True,
#         stdin=False,
#         stdout=True,
#         tty=False
#     )
    
def connect_get_namespaced_pod_exec(pod_name: str, command: str, namespace: str = "nautilus"):
    wrapped_command = ["/bin/bash", "-c", command]
    return stream(
        v1.connect_get_namespaced_pod_exec,
        name=pod_name,
        namespace=namespace,
        command=wrapped_command,
        stderr=True,
        stdin=False,
        stdout=True,
        tty=False
    )

    
def connect_get_namespaced_pod_portforward(namespace: str, pod_name: str, ports: list):
    """Pod의 포트를 포트포워딩"""
    return v1.connect_get_namespaced_pod_portforward(pod_name, namespace, ports=ports)

def connect_get_namespaced_service_proxy(namespace: str, service_name: str):
    """특정 Service에 Proxy 연결"""
    return v1.connect_get_namespaced_service_proxy(service_name, namespace)

def copy_to_container(pod_name: str, namespace: str, local_file_path: str, container_path: str, type: str = "file"):
    """
    주어진 파일을 Kubernetes Pod 내 컨테이너로 복사하는 함수.
    
    :param pod_name: 파일을 복사할 Pod의 이름
    :param namespace: Pod가 속한 namespace
    :param local_file_path: 로컬 시스템에서 복사할 파일 경로
    :param container_path: 컨테이너 내에서 복사할 대상 경로
    :param type: "file" 또는 "folder" (기본값: "file")
    """
    try:
        if type == "file":
            command = [
                "kubectl", "cp", local_file_path,
                f"{namespace}/{pod_name}:{container_path}"
            ]
        elif type == "folder":
            command = [
                "kubectl", "cp", "-r", local_file_path,
                f"{namespace}/{pod_name}:{container_path}"
            ]
        else: 
            print(f"[ERROR] Undefined type: {type}")
            return
        
        print(f"[INFO] Running command: {' '.join(command)}")  # 디버깅용 로그 추가
        subprocess.run(command, check=True)
        print(f"[SUCCESS] File successfully copied to {pod_name} in container!")

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] File copy failed: {e}")
        print(f"[DEBUG] Check if pod exists: kubectl get pods -n {namespace}")
        print(f"[DEBUG] Check if namespace exists: kubectl get ns")
        
        
if __name__ == "__main__":
    f = open('api_result.json', 'w')

    print("########################### Print Nodes : ", file=f)
    print(list_node(), file=f)
    print("########################### Print Pod : ", file=f)
    print(list_pod_for_all_namespaces(), file=f)
    print("########################### Print Deployment : ", file=f)
    print(list_deployment_for_all_namespace(), file=f)

