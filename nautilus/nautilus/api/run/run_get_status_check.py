import os
import sys
import pexpect
from typing import List, Dict

# 📌 루트 경로 등록
ROOT_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT_BASE_DIR)


def run_nvflare_job_in_pod(pod_name: str, project_id: str) -> str:
    """
    NVFLARE Admin Console에서 check_status client 명령 실행 후 결과 반환
    """
    admin_script_path = f"/workspace/nautilus/nautilus/workspace/provision/{project_id}/prod_00/admin@nvidia.com/startup/fl_admin.sh"
    cmd = f"kubectl exec -i {pod_name} -- {admin_script_path}"
    print(f"\n🔧 [실행 명령어]: {cmd}\n")

    child = pexpect.spawn(cmd, encoding='utf-8', timeout=30)

    child.expect("User Name:")
    child.sendline("admin@nvidia.com")

    child.expect(">")
    child.sendline("check_status client")

    child.expect("Done")
    output = child.before

    print("\n📄 [명령어 원본 출력]:\n")
    print(output)  # 전체 원본 출력

    return output


def parse_check_status_output(output: str) -> List[Dict[str, str]]:
    lines = output.strip().splitlines()

    # '|' 로 시작하고 끝나는 줄만 필터링
    content_lines = [line for line in lines if line.strip().startswith('|') and line.strip().endswith('|')]
    print("\n✅ 테이블 필터링된 줄:\n", content_lines)

    if len(content_lines) < 2:
        print("⚠️ 테이블 구조가 부족합니다.")
        return []

    header_line = content_lines[0]
    headers = [h.strip().lower().replace(" ", "_") for h in header_line.strip('|').split('|')]

    results = []
    for line in content_lines[1:]:  # 나머지는 데이터 줄
        cols = [c.strip() for c in line.strip('|').split('|')]
        print(f"\n🔍 현재 줄 파싱:\n{line}\n➡️ 값 목록: {cols}")

        if len(cols) != len(headers):
            print(f"⚠️ 열 개수가 헤더와 맞지 않음 → 건너뜀: {cols}")
            continue

        row = dict(zip(headers, cols))
        print("✅ 변환된 딕셔너리:", row)
        results.append(row)

    return results


def check_client_status(project_id: str) -> List[Dict[str, str]]:
    #pod_name = f"{project_id}-server"
    pod_name = "mylocalhost"
    raw_output = run_nvflare_job_in_pod(pod_name=pod_name, project_id=project_id)
    return parse_check_status_output(raw_output)


# CLI 실행
if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Check NVFLARE client status")
    parser.add_argument("--project_id", type=str, required=True, help="Project ID")
    args = parser.parse_args()

    result = check_client_status(args.project_id)

    print("\n📦 [JSON 포맷 결과]:\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
