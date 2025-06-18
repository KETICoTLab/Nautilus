from typing import List, Optional
from app.schemas.data_provider import DataProviderCreate, DataProvider, DataProviderResponse, DataProviderDataCreate, DataProviderData, HostInformation
from app.service.base import fetch_one, fetch_all, execute
from datetime import datetime, timezone
import json
import os
import subprocess
from pathlib import Path
from app.config import HOST
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
    yml_content = (
        f'ansible_become_password: "{password}"\n'
        f'ansible_ssh_user: "{username}"\n'
        f'ansible_ssh_password: "{password}"\n'
    )

    # YAML 파일 저장
    with open(host_vars_path, "w", encoding="utf-8") as yml_file:
        yml_file.write(yml_content)

    # Ansible Vault를 사용하여 파일 암호화
    subprocess.run(
        ["ansible-vault", "encrypt", "--vault-password-file", str(vault_password_path), str(host_vars_path)],
        check=True
    )
    
    run_join_playbook(ip_address, str(data_provider_id), str(HOST))#master pc ip적어줘야 함.
    
    
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


from pydantic import ValidationError
import json

async def update_data_provider(data_provider_id: str, data: DataProviderCreate, pool) -> Optional[DataProvider]:
    field_map = {
        "data_provider_name": data.data_provider_name,
        "description": data.description,
        "tags": data.tags,
        "creator_id": data.creator_id,
        "train_code_path": data.train_code_path,
        "train_data_path": data.train_data_path,
    }

    # ✅ host_information 처리
    host_info = data.host_information
    if host_info is not None:
        if isinstance(host_info, str):
            try:
                host_info = HostInformation(**json.loads(host_info))
            except (json.JSONDecodeError, ValidationError) as e:
                raise ValueError(f"Invalid host_information format: {e}")
        # ✅ PostgreSQL JSONB에 넣기 위해 문자열로 직렬화
        field_map["host_information"] = host_info.json()

    # ✅ 쿼리 동적 생성
    set_clauses = []
    values = []
    idx = 1
    for key, value in field_map.items():
        if value is not None:
            set_clauses.append(f"{key} = ${idx}")
            values.append(value)
            idx += 1

    set_clauses.append("modification_time = NOW()")
    values.append(data_provider_id)

    query = f"""
    UPDATE data_providers
    SET {', '.join(set_clauses)}
    WHERE data_provider_id = ${idx}
    RETURNING *;
    """

    row = await fetch_one(pool, query, *values)

    # ✅ asyncpg.Record → dict 변환 후 처리
    if row:
        row_dict = dict(row)
        if isinstance(row_dict.get("host_information"), str):
            row_dict["host_information"] = HostInformation(**json.loads(row_dict["host_information"]))
        return DataProvider(**row_dict)

    return None



async def delete_data_provider(data_provider_id: str, pool) -> bool:
    # host_ip 조회
    row = await fetch_one(pool, "SELECT host_information FROM data_providers WHERE data_provider_id = $1;", data_provider_id)
    if not row:
        return False

    host_info = json.loads(row["host_information"])
    ip_address = host_info.get("ip_address")
    if not ip_address:
        raise ValueError("Missing ip_address in host_information")

    # Step 1: 종속된 데이터 삭제
    await execute(pool, "DELETE FROM data WHERE data_provider_id = $1;", data_provider_id)

    # Step 2: provider 삭제
    result = await execute(pool, "DELETE FROM data_providers WHERE data_provider_id = $1;", data_provider_id)

    # Step 3: ansible host_vars 파일 삭제
    host_vars_path = Path(ANSIBLE_HOST_VARS_DIR).resolve() / f"{ip_address}.yml"
    if host_vars_path.exists():
        host_vars_path.unlink()  # 파일 삭제
        print(f"🗑️ Deleted host_vars: {host_vars_path}")

    return "DELETE" in result and result.endswith("1")

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
        dp.data_provider_id,
        dp.data_provider_name,
        dp.description AS provider_description,
        dp.tags,
        dp.creator_id,
        dp.train_code_path,
        dp.train_data_path,

        d.data_id,
        d.item_code_id,
        d.data_name,
        d.description,
        d.data

    FROM data_providers dp
    LEFT JOIN data d ON dp.data_provider_id = d.data_provider_id;
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

        # data가 없는 경우도 포함되도록 처리
        data = DataProviderData(
            data_id=row_dict.get("data_id"),
            item_code_id=row_dict.get("item_code_id"),
            data_name=row_dict.get("data_name"),
            description=row_dict.get("description"),
            data=row_dict.get("data"),
            data_provider=data_provider
        )

        result.append(data)

    return result

async def delete_data_provider_data(data_provider_id: str, data_id: str, pool) -> bool:
    query = "DELETE FROM data WHERE data_provider_id = $1 and data_id = $2;"
    result = await execute(pool, query, data_provider_id, data_id)
    return result.endswith("DELETE 1")


async def update_data_provider_data(data_provider_id: str, data_id:str, data: DataProviderDataCreate, pool) -> Optional[DataProviderData]:
    field_map = {
        "item_code_id": data.item_code_id,
        "data_name": data.data_name,
        "description": data.description,
        "data": data.data,
    }

    set_clauses = []
    values = []
    idx = 1
    for key, value in field_map.items():
        if value is not None:
            set_clauses.append(f"{key} = ${idx}")
            values.append(value)
            idx += 1

    # 마지막으로 data_id 조건 추가
    values.append(data_id)
    query = f"""
    UPDATE data
    SET {', '.join(set_clauses)}
    WHERE data_id = ${idx}
    RETURNING *;
    """

    row = await fetch_one(pool, query, *values)

    return DataProviderData(**dict(row)) if row else None