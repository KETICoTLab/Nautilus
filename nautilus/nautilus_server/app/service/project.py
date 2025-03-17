from typing import List, Optional
from app.schemas.project import ProjectCreate, Project
from app.service.base import fetch_one, fetch_all, execute
from datetime import datetime, timezone
import subprocess

async def create_project(data: ProjectCreate, pool):
    """
    number_of_client가 있으면 provision.py실행
    """
    project_id = "P-KR-" + data.project_name
    
    query = """
    INSERT INTO projects (project_id, project_name, description, tags, creator_id, data_provider_ids, number_of_clients, number_of_jobs, number_of_subscriptions, project_image, creation_time, modification_time)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW(), NOW())
    RETURNING *;
    """
    row = await fetch_one(pool, query, project_id, data.project_name, data.description, data.tags, data.creator_id, data.data_provider_ids, data.number_of_clients, data.number_of_jobs, data.number_of_subscriptions, data.project_image)
    
    # provision.py 실행 (비동기 실행)
    provision_script = "../nautilus/api/run/provision.py"  # nautilus/ 디렉토리에 위치
    provision_command = [
        "python", provision_script,
        "--project_id", project_id,
        "--project_name", data.project_name,
        "--number_of_client", str(data.number_of_clients)
    ]

    print(f"Running provision.py: {' '.join(provision_command)}")
    
    try:
        # * 실시간 로그 출력하도록 변경
        process = subprocess.Popen(
            provision_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # * 문자열로 변환하여 실시간 출력
        )

        # * 표준 출력 및 오류 로그 실시간 출력
        for line in process.stdout:
            print(f"[provision.py LOG]: {line.strip()}")

        for line in process.stderr:
            print(f"[provision.py ERROR]: {line.strip()}")

        process.wait()  # * 프로세스 종료까지 대기
        print(f"* provision.py finished with exit code {process.returncode}")

    except Exception as e:
        print(f"* provision failed: {e}")
        
    return Project(**row)

async def get_project(project_id: str) -> Optional[Project]:
    query = "SELECT * FROM projects WHERE project_id = $1;"
    row = await fetch_one(pool, query, project_id)
    return Project(**row) if row else None

async def update_project(project_id: str, data: ProjectCreate) -> Optional[Project]:
    """
    data_provider_ids가 있으면 등록된 provider의 host-ip, data_provider_name 조회 하여 인자 전달 validation.py실행
    """
    
    
    
    query = """
    UPDATE projects
    SET project_name = $1, description = $2, tags = $3, creator_id = $4, number_of_clients = $5, number_of_jobs = $6, number_of_subscriptions = $7, project_image = $8, modification_time = NOW()
    WHERE project_id = $9
    RETURNING *;
    """
    row = await fetch_one(pool, query, data.project_name, data.description, data.tags, data.creator_id, data.number_of_clients, data.number_of_jobs, data.number_of_subscriptions, data.project_image, project_id)
    return Project(**row) if row else None

async def delete_project(project_id: str) -> bool:
    query = "DELETE FROM projects WHERE project_id = $1;"
    result = await execute(pool, query, project_id)
    return result.endswith("DELETE 1")

async def list_projects() -> List[Project]:
    query = "SELECT * FROM projects;"
    rows = await fetch_all(pool, query)
    return [Project(**row) for row in rows]


async def validation_check(project_id: str):
    # provision.py 실행 (비동기 실행)
    provision_script = "../nautilus/api/run/validation_deploy.py"  # nautilus/ 디렉토리에 위치
    config_name = f"{project_id}_config.json"
    validation_check_command = [
        "python", provision_script,
        "--config", config_name
    ]

    print(f"Running provision.py: {' '.join(validation_check_command)}")
    
    try:
        # * 실시간 로그 출력하도록 변경
        process = subprocess.Popen(
            validation_check_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # * 문자열로 변환하여 실시간 출력
        )

        # * 표준 출력 및 오류 로그 실시간 출력
        for line in process.stdout:
            print(f"[validation_check.py LOG]: {line.strip()}")

        for line in process.stderr:
            print(f"[validation_check.py ERROR]: {line.strip()}")

        process.wait()  # * 프로세스 종료까지 대기
        print(f"* validation_check.py finished with exit code {process.returncode}")

    except Exception as e:
        print(f"* validation_check failed: {e}")
        
    return "validation_check"