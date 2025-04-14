# run_get_status_check_container.py (docker-compose 환경용)

import os
import sys
import pexpect
from typing import List, Dict

# 📌 루트 경로 등록
ROOT_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT_BASE_DIR)

def run_nvflare_job_in_container(container_name: str, project_id: str) -> str:
    """
    docker-compose로 띄운 NVFLARE Admin Console 컨테이너에서 check_status client 실행
    """
    admin_script_path = f"/workspace/nautilus/nautilus/workspace/provision/{project_id}/prod_00/admin@nvidia.com/startup/fl_admin.sh"
    cmd = f"docker exec -i {container_name} {admin_script_path}"
    print(f"📦 실행 명령어: {cmd}")
    child = pexpect.spawn(cmd, encoding='utf-8', timeout=30)

    try:
        child.expect("User Name:")
        child.sendline("admin@nvidia.com")

        child.expect(">")
        child.sendline("check_status client")

        child.expect("Done")
        output = child.before
        return output

    except pexpect.exceptions.EOF:
        return "❌ EOF 발생 - 컨테이너가 예상대로 응답하지 않음"
    except pexpect.exceptions.TIMEOUT:
        return "❌ Timeout 발생 - 컨테이너 명령 실행 시간 초과"
    finally:
        child.close()


def parse_check_status_output(output: str) -> List[Dict[str, str]]:
    lines = output.strip().splitlines()

    # '|' 로 시작하고 끝나는 줄만 필터링
    content_lines = [line for line in lines if line.strip().startswith('|') and line.strip().endswith('|')]

    if len(content_lines) < 2:
        print("⚠️ 테이블 구조가 부족합니다.")
        return []

    header_line = content_lines[0]
    headers = [h.strip().lower().replace(" ", "_") for h in header_line.strip('|').split('|')]

    results = []
    for line in content_lines[1:]:  # 나머지는 데이터 줄
        cols = [c.strip() for c in line.strip('|').split('|')]

        if len(cols) != len(headers):
            print(f"⚠️ 열 개수가 헤더와 맞지 않음 → 건너뜀: {cols}")
            continue

        row = dict(zip(headers, cols))
        results.append(row)

    return results


def check_client_status(project_id: str) -> List[Dict[str, str]]:
    container_name = "mylocalhost"  # docker-compose에서 설정한 서버 컨테이너 이름
    raw_output = run_nvflare_job_in_container(container_name=container_name, project_id=project_id)
    return parse_check_status_output(raw_output)


# CLI 실행
if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Check NVFLARE client status via Docker")
    parser.add_argument("--project_id", type=str, required=True, help="Project ID")
    args = parser.parse_args()

    result = check_client_status(args.project_id)

    print("\n📦 [JSON 포맷 결과]:\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
