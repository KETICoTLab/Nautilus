import uuid 
from datetime import datetime
from app.schemas.client import ClientCreate, ClientResponse, CheckStatusUpdate
from app.service.base import fetch_one, fetch_all, execute
import json
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")) #Nautilus/nautilus
print(f"service/client.py) BASE_DIR resolved to: {BASE_DIR}")
async def create_client(project_id: str, client_data: ClientCreate, pool):
    client_id = "C-KR-" + client_data.client_name
        
    # `data_id`를 사용하여 `data_providers`에서 `host_information` 및 `data_provider_id` 조회
    provider_query = """
    SELECT dp.data_provider_id, dp.host_information
    FROM data_providers dp
    JOIN data d ON dp.data_provider_id = d.data_provider_id
    WHERE d.data_id = $1;
    """
    provider_row = await fetch_one(pool, provider_query, client_data.data_id)

    if not provider_row or "host_information" not in provider_row:
        raise Exception(f"No host_information found for data_id: {client_data.data_id}")

    data_provider_id = provider_row["data_provider_id"]
    host_information = json.loads(provider_row["host_information"])
    ip_address = host_information.get("ip_address")

    if not ip_address:
        raise Exception(f"No IP address found in host_information for data_id: {client_data.data_id}")

    # Config 파일 경로
    config_path = os.path.join(BASE_DIR, "nautilus", "workspace", "configs", f"{project_id}_config.json")
    print(f"[DEBUG] Absolute config_path: {config_path}")

    # 기존 `config.json` 파일 로드
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config_data = json.load(f)
    else:
        config_data = {"project_id": project_id, "target_hosts": [], "client_info": {}, "nodes": [], "client_list": []}

    # `target_hosts` 및 `client_list`에 추가
    if ip_address not in config_data["target_hosts"]:
        config_data["target_hosts"].append(ip_address)
        config_data["client_list"].append(client_id)
        site_index = len(config_data["target_hosts"])
        config_data["client_info"][f"site-{site_index}"] = client_data.data_id

    # `nodes`에 `data_provider_id` 추가 (중복 확인 없이 항상 추가)
    config_data["nodes"].append(data_provider_id)

    # 변경된 `config.json` 저장
    with open(config_path, "w") as f:
        json.dump(config_data, f, indent=4)
    
    # 클라이언트 생성 SQL
    client_query = """
    INSERT INTO clients (client_id, project_id, job_id, client_name, data_id, creation_time)
    VALUES ($1, $2, $3, $4, $5, NOW())
    RETURNING *;
    """
    client_row = await fetch_one(pool, client_query, client_id, project_id, client_data.job_id, client_data.client_name, client_data.data_id)

    # check-status 생성
    check_status_id = "CH-KR-"+ str(uuid.uuid4())[:8]
    status_query = """
    INSERT INTO check_status (check_status_id, client_id, validation_status, termination_status, creation_time)
    VALUES ($1, $2, -1, -1, NOW())
    RETURNING *;
    """
    await fetch_one(pool, status_query, check_status_id, client_id)

    return ClientResponse(**dict(client_row))


async def get_clients(project_id: str, name: str = None, pool=None):
    """특정 프로젝트의 모든 클라이언트 조회"""
    query = "SELECT * FROM clients WHERE project_id = $1"
    params = [project_id]

    if name:
        query += " AND client_name ILIKE $2"
        params.append(f"%{name}%")

    return await fetch_all(pool, query, *params)

async def get_client(client_id: str, pool):
    """클라이언트 ID로 클라이언트 정보 조회"""
    query = "SELECT * FROM clients WHERE client_id = $1"
    return await fetch_one(pool, query, client_id)

async def update_check_status(project_id: str, client_id: str, status_data: CheckStatusUpdate, pool):
    """클라이언트의 check-status 업데이트. COALESCE()를 사용하여 None 값이 들어오면 기존 값을 유지"""
    query = """
    UPDATE check_status
    SET validation_status = COALESCE($1, validation_status),
        termination_status = COALESCE($2, termination_status)
    WHERE client_id = $3
    RETURNING *;
    """
    print(status_data)
    return await fetch_one(pool, query, status_data.validation_status, status_data.termination_status, client_id)
