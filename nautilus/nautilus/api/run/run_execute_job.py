# run_create_job
import os  
import json
import argparse
import subprocess
import sys
import pexpect

# 📌 ROOT_BASE_DIR `nautilus` 루트 디렉토리로 설정
ROOT_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT_BASE_DIR)
from nautilus.core.communicate.validation import (
    execute_command
)
from nautilus.core.communicate.k8s import (
    get_pod_name_by_deployment
)

def run_nvflare_job_in_pod(pod_name: str, project_id: str, job_id: str, namespace: str = "nautilus"):
    cmd = f"kubectl exec -i {pod_name} -n {namespace} -- /workspace/nautilus/nautilus/workspace/provision/{project_id}/prod_00/admin@nvidia.com/startup/fl_admin.sh"
    print(f"- Executing (cmd): {cmd}")
    child = pexpect.spawn(cmd, encoding='utf-8')

    child.expect("User Name:")
    child.sendline("admin@nvidia.com")

    child.expect(">")
    child.sendline(f"submit_job /workspace/nautilus/nautilus/workspace/jobs/{job_id}")

    child.expect("Done")
    print(child.before)


def main(project_id, job_id, namespace):
    pod_name = f"{project_id}-server"
    print(f"Starting execute job for Project: {project_id}")
    '''
    server_pod_name = f"{project_id}-server"
    server_pod_full_name = get_pod_name_by_deployment(deployment_name=server_pod_name)
    print(f"Deploying Server | Pod: {server_pod_name} | pod_full_name: {server_pod_full_name}")    
    '''
    run_nvflare_job_in_pod(pod_name="mylocalhost", project_id=project_id, job_id=job_id, namespace=namespace)
        
    print("Job execution completed successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy Nautilus Federated Learning Simulation")
    parser.add_argument("--project_id", type=str, required=True, help="Project ID")
    parser.add_argument("--job_id", type=str, required=True, help="Job ID")
    parser.add_argument("--namespace", type=str, default="nautilus", help="Kubernetes namespace (default: nautilus)")

    args = parser.parse_args()

    main(args.project_id, args.job_id, args.namespace)