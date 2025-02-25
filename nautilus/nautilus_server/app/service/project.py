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
    provision_script = "../provision.py"  # nautilus/ 디렉토리에 위치
    provision_command = [
        "python", provision_script,
        "--project_id", project_id,
        "--project_name", data.project_name,
        "--number_of_client", str(data.number_of_clients)
    ]

    print(f"Running provision.py: {' '.join(provision_command)}")
    
    try:
        subprocess.Popen(provision_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        print(f"Provisioning failed: {e}")
        
    return Project(**row)

async def get_project(project_id: int) -> Optional[Project]:
    query = "SELECT * FROM projects WHERE project_id = $1;"
    row = await fetch_one(pool, query, project_id)
    return Project(**row) if row else None

async def update_project(project_id: int, data: ProjectCreate) -> Optional[Project]:
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

async def delete_project(project_id: int) -> bool:
    query = "DELETE FROM projects WHERE project_id = $1;"
    result = await execute(pool, query, project_id)
    return result.endswith("DELETE 1")

async def list_projects() -> List[Project]:
    query = "SELECT * FROM projects;"
    rows = await fetch_all(pool, query)
    return [Project(**row) for row in rows]
