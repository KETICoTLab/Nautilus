# run_exec_job_container
import os
import sys
import argparse
import pexpect

# 📌 프로젝트 루트 디렉토리 설정
ROOT_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT_BASE_DIR)

def run_nvflare_job_in_container(container_name: str, project_id: str, job_id: str):
    """
    docker-compose로 띄운 컨테이너에 명령어를 실행하여 job submit 수행
    """
    cmd = f"docker exec -i {container_name} /workspace/nautilus/nautilus/workspace/provision/{project_id}/prod_00/admin@nvidia.com/startup/fl_admin.sh"
    print(f"- Executing (cmd): {cmd}")
    child = pexpect.spawn(cmd, encoding='utf-8')

    try:
        child.expect("User Name:")
        child.sendline("admin@nvidia.com")

        child.expect(">")
        child.sendline(f"submit_job /workspace/nautilus/nautilus/workspace/jobs/{job_id}")

        child.expect("Done")
        print("✅ Job submitted successfully.")
        print(child.before)
    except pexpect.exceptions.EOF:
        print("❌ Unexpected end of output from container.")
    except pexpect.exceptions.TIMEOUT:
        print("❌ Timeout while communicating with container.")
    finally:
        child.close()


def main(project_id: str, job_id: str):
    container_name = "mylocalhost"  # docker-compose 기준 서버 컨테이너 이름
    print(f"🚀 Starting NVFLARE job in container: {container_name}")
    run_nvflare_job_in_container(container_name, project_id, job_id)
    print("🏁 Job execution completed!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute NVFLARE Job via Docker")
    parser.add_argument("--project_id", type=str, required=True, help="Project ID")
    parser.add_argument("--job_id", type=str, required=True, help="Job ID")

    args = parser.parse_args()
    main(args.project_id, args.job_id)
