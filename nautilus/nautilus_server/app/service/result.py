from typing import List, Optional
from app.service.base import fetch_one, fetch_all, execute
from datetime import datetime, timezone
import uuid

async def create_result(data, pool):
    result_id = str(uuid.uuid4())[:8]
    query = """
    INSERT INTO results (result_id, data, creation_time)
    VALUES ($1, $2, NOW())
    RETURNING *;
    """
    row = await fetch_one(pool, query, result_id, data)
    #data type 맞춰서 DBtable생성 필요
    return result(**row)

async def get_result():
    query = "SELECT * FROM results;"
    row = await fetch_one(pool, query, result_id)
    return result(**row) if row else None
