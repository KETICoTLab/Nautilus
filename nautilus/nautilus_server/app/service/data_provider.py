from typing import List, Optional
from app.schemas.data_provider import DataProviderCreate, DataProvider , DataProviderDataCreate, DataProviderData
from app.service.base import fetch_one, fetch_all, execute
from datetime import datetime, timezone
import json

async def create_data_provider(data: DataProviderCreate, pool) -> DataProvider:
    data_provider_id = "W-KR-"+ data.data_provider_name
    host_information_json = json.dumps(data.host_information.dict())
    
    query = """
    INSERT INTO data_providers (data_provider_id, data_provider_name, description, tags, creator_id, creation_time, host_information, train_code_path, train_data_path)
    VALUES ($1, $2, $3, $4, $5, NOW(), $6, $7, $8)
    RETURNING *;
    """
    row = await fetch_one(pool, query, data_provider_id, data.data_provider_name, data.description, data.tags, data.creator_id, host_information_json, data.train_code_path, data.train_data_path)
    row_dict = dict(row)
    row_dict["host_information"] = json.loads(row_dict["host_information"])  # JSON 문자열을 다시 객체로 변환

    return DataProvider(**row_dict)

async def get_data_provider(data_provider_id: str) -> Optional[DataProvider]:
    query = "SELECT * FROM data_providers WHERE data_provider_id = $1;"
    row = await fetch_one(pool, query, data_provider_id)
    return DataProvider(**row) if row else None

async def update_data_provider(data_provider_id: str, data: DataProviderCreate) -> Optional[DataProvider]:
    query = """
    UPDATE data_providers
    SET data_provider_name = $1, description = $2, tags = $3, creator_id = $4, host_information = $5, train_code_path = $6, train_data_path = $7, modification_time = NOW()
    WHERE data_provider_id = $8
    RETURNING *;
    """
    row = await fetch_one(pool, query, data.data_provider_name, data.description, data.tags, data.creator_id, data.host_information, data.train_code_path, data.train_data_path, data_provider_id)
    return DataProvider(**row) if row else None

async def delete_data_provider(data_provider_id: str) -> bool:
    query = "DELETE FROM data_providers WHERE data_provider_id = $1;"
    result = await execute(pool, query, data_provider_id)
    return result.endswith("DELETE 1")

async def list_data_providers() -> List[DataProvider]:
    query = "SELECT * FROM data_providers;"
    rows = await fetch_all(pool, query)
    return [DataProvider(**row) for row in rows]


async def create_data_provider_data(data_provider_id: str, data: DataProviderDataCreate, pool) -> DataProviderData:
    from app.database import pool
    data_id = "D-KR-"+data.data_name
    creation_time = datetime.now(timezone.utc)
    query = """
    INSERT INTO data (data_id, data_provider_id, item_code_id, data_name, description, creation_time, data)
    VALUES ($1, $2, $3, $4, $5, $6, $7)
    RETURNING *;
    """
    row = await fetch_one(pool, query, data_id, data_provider_id, data.item_code_id, data.data_name, data.description, creation_time, data.data)
    return DataProviderData(**row)

async def get_data_provider_data(data_provider_id: str, data_id: str) -> Optional[DataProviderData]:
    query = "SELECT * FROM data WHERE data_provider_id = $1 and data_id = $2;"
    row = await fetch_one(pool, query, data_provider_id)
    return DataProviderData(**row) if row else None

async def delete_data_provider_data(data_provider_id: str, data_id: str) -> bool:
    query = "DELETE FROM data WHERE data_provider_id = $1 and data_id = $2;"
    result = await execute(pool, query, data_provider_id)
    return result.endswith("DELETE 1")

