from typing import List, Optional
from app.schemas.data_provider import DataProviderCreate, DataProvider, DataProviderResponse, DataProviderDataCreate, DataProviderData, HostInformation
from app.service.base import fetch_one, fetch_all, execute
from datetime import datetime, timezone
import json
import os
import subprocess
from pathlib import Path

import sys

# `nautilus` 디렉토리를 Python 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from nautilus.core.communicate.validation import run_join_playbook  

ANSIBLE_VAULT_PASS_PATH = "../nautilus/workspace/ansible_project/inventory/host_vars/vaultpass"
ANSIBLE_HOST_VARS_DIR = "../nautilus/workspace/ansible_project/inventory/host_vars"

async def create_data_provider(data: DataProviderCreate, pool) -> DataProvider:
    data_provider_id = "w-kr-" + data.data_provider_name
    host_information_json = json.dumps(data.host_information.dict())

    query = """
    INSERT INTO data_providers (data_provider_id, data_provider_name, description, tags, creator_id, creation_time, host_information, train_code_path, train_data_path)
    VALUES ($1, $2, $3, $4, $5, NOW(), $6, $7, $8)
    RETURNING *;
    """
    row = await fetch_one(pool, query, data_provider_id, data.data_provider_name, data.description, data.tags, data.creator_id, host_information_json, data.train_code_path, data.train_data_path)
    
    row_dict = dict(row)
    row_dict["host_information"] = json.loads(row_dict["host_information"])  # JSON 문자열을 다시 객체로 변환

    # Ansible host_vars YAML 파일 생성
    await create_ansible_host_vars(row_dict["host_information"], data_provider_id)

    return DataProvider(**row_dict)


async def create_ansible_host_vars(host_information, data_provider_id):
    """
    Ansible host_vars 폴더에 해당 호스트의 yml 파일을 생성하고 암호화함.
    """
    ip_address = host_information["ip_address"]
    username = host_information["username"]
    password = host_information["password"]

    host_vars_dir = Path(ANSIBLE_HOST_VARS_DIR).resolve()
    vault_password_path = Path(ANSIBLE_VAULT_PASS_PATH).resolve()
    
    # 디렉토리 생성
    host_vars_dir.mkdir(parents=True, exist_ok=True)

    host_vars_path = host_vars_dir / f"{ip_address}.yml"

    # yml 파일 내용 생성
    yml_content = f"""ansible_become_password: "{password}"
                ansible_ssh_user: "{username}"
                ansible_ssh_password: "{password}"
                """

    # YAML 파일 저장
    with open(host_vars_path, "w", encoding="utf-8") as yml_file:
        yml_file.write(yml_content)

    # Ansible Vault를 사용하여 파일 암호화
    subprocess.run(
        ["ansible-vault", "encrypt", "--vault-password-file", str(vault_password_path), str(host_vars_path)],
        check=True
    )
    
    run_join_playbook(ip_address, str(data_provider_id), str("master_node_ip"))#master pc ip적어줘야 함.
    
    
async def get_data_provider(data_provider_id: str, pool) -> Optional[DataProviderResponse]:
    query = "SELECT * FROM data_providers WHERE data_provider_id = $1;"
    row = await fetch_one(pool, query, data_provider_id)

    if not row:
        return None
    
    row_dict = dict(row)
    if isinstance(row_dict.get("host_information"), str):
        row_dict["host_information"] = json.loads(row_dict["host_information"])

    # ✅ host_information 제거
    row_dict.pop("host_information", None)

    return DataProviderResponse(**row_dict)

async def update_data_provider(data_provider_id: str, data: DataProviderCreate, pool) -> Optional[DataProvider]:
    query = """
    UPDATE data_providers
    SET data_provider_name = $1, description = $2, tags = $3, creator_id = $4, host_information = $5, train_code_path = $6, train_data_path = $7, modification_time = NOW()
    WHERE data_provider_id = $8
    RETURNING *;
    """
    row = await fetch_one(pool, query, data.data_provider_name, data.description, data.tags, data.creator_id, data.host_information, data.train_code_path, data.train_data_path, data_provider_id)
    return DataProvider(**row) if row else None

async def delete_data_provider(data_provider_id: str, pool) -> bool:
    query = "DELETE FROM data_providers WHERE data_provider_id = $1;"
    result = await execute(pool, query, data_provider_id)
    return result.endswith("DELETE 1")

async def list_data_providers(pool) -> List[DataProviderResponse]:
    query = "SELECT * FROM data_providers;"
    rows = await fetch_all(pool, query)
    providers = []

    for row in rows:
        data = dict(row)

        if isinstance(data.get("host_information"), str):
            try:
                data["host_information"] = json.loads(data["host_information"])
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format in host_information")

        providers.append(DataProviderResponse(**data))
    return providers


async def create_data_provider_data(data_provider_id: str, data: DataProviderDataCreate, pool) -> DataProviderData:
    from app.database import pool
    data_id = "d-kr-"+data.data_name
    creation_time = datetime.now(timezone.utc)
    query = """
    INSERT INTO data (data_id, data_provider_id, item_code_id, data_name, description, creation_time, data)
    VALUES ($1, $2, $3, $4, $5, $6, $7)
    RETURNING *;
    """
    row = await fetch_one(pool, query, data_id, data_provider_id, data.item_code_id, data.data_name, data.description, creation_time, data.data)
    return DataProviderData(**row)

async def list_data_provider_data(data_provider_id: str, pool) -> List[DataProviderData]:
    query = """
        SELECT data_id, item_code_id, data_name, description, data
        FROM data WHERE data_provider_id = $1 ;
    """
    rows = await fetch_all(pool, query, data_provider_id)

    return [DataProviderData(**dict(row)) for row in rows]


async def list_data_provider_data_all(pool) -> List[DataProviderData]:
    query = """
    SELECT
        d.data_id,
        d.data_provider_id,
        d.item_code_id,
        d.data_name,
        d.description,
        d.data,

        dp.data_provider_id,
        dp.data_provider_name,
        dp.description AS provider_description,
        dp.tags,
        dp.creator_id,
        dp.train_code_path,
        dp.train_data_path

    FROM data d
    JOIN data_providers dp
      ON d.data_provider_id = dp.data_provider_id;
    """
    rows = await fetch_all(pool, query)

    result = []
    for row in rows:
        row_dict = dict(row)

        data_provider = DataProvider(
            data_provider_id=row_dict["data_provider_id"],
            data_provider_name=row_dict["data_provider_name"],
            description=row_dict["provider_description"],
            tags=row_dict["tags"],
            creator_id=row_dict["creator_id"],
            train_code_path=row_dict["train_code_path"],
            train_data_path=row_dict["train_data_path"]
        )

        data = DataProviderData(
            data_id=row_dict["data_id"],
            item_code_id=row_dict["item_code_id"],
            data_name=row_dict["data_name"],
            description=row_dict["description"],
            data=row_dict["data"],
            data_provider=data_provider  # ✅ 중첩 객체 포함
        )

        result.append(data)

    return result

async def delete_data_provider_data(data_provider_id: str, data_id: str, pool) -> bool:
    query = "DELETE FROM data WHERE data_provider_id = $1 and data_id = $2;"
    result = await execute(pool, query, data_provider_id, data_id)
    return result.endswith("DELETE 1")

