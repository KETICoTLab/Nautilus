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
    """
    check_status client 명령 결과를 파싱하여 딕셔너리 리스트로 반환
    """
    lines = [line.strip() for line in output.strip().splitlines()]
    content_lines = [line for line in lines if line.startswith("|") and line.endswith("|")]

    if len(content_lines) < 3:
        print("⚠️ 테이블 형식이 올바르지 않음 (헤더 또는 구분선 부족)")
        return []

    header_line = content_lines[1]
    headers = [h.strip().lower().replace(" ", "_") for h in header_line.strip("|").split("|")]

    results = []
    for line in content_lines[2:-1]:  # 데이터 줄만 처리
        cols = [col.strip() for col in line.strip("|").split("|")]
        if len(cols) != len(headers):
            print(f"⚠️ 열 개수 불일치 → 무시됨: {cols}")
            continue
        row = dict(zip(headers, cols))
        results.append(row)

    print("\n✅ [파싱된 결과]:\n")
    for r in results:
        print(r)

    return results


def check_client_status(project_id: str) -> List[Dict[str, str]]:
    #pod_name = f"{project_id}-server"
    pod_name = mylocalhost
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
