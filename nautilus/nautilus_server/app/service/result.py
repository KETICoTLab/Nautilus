from typing import List, Optional
from app.service.base import fetch_one, fetch_all, execute
from app.schemas.result import ResultCreate, Result
from datetime import datetime, timezone
import uuid
import json

async def create_result(data, pool):
    result_id = str(uuid.uuid4())[:8]

    query = """
    INSERT INTO results (result_id, data, creation_time)
    VALUES ($1, $2::jsonb, NOW())
    RETURNING *;
    """
    json_data = json.dumps(data.data)  # `data.data` 값을 추출하여 JSON 직렬화
    row = await fetch_one(pool, query, result_id, json_data)

    # ✅ PostgreSQL 결과를 FastAPI의 `Result` 모델과 일치하도록 변환
    return Result(
        result_id=row["result_id"],
        data=json.loads(row["data"]),  # JSON 문자열을 다시 객체로 변환
        creation_time=row["creation_time"]
    )

async def get_result(pool):
    query = "SELECT result_id, data, creation_time FROM results;"
    rows = await fetch_all(pool, query)

    # ✅ 데이터를 FastAPI의 `Result` 모델에 맞게 변환
    results = []
    for row in rows:
        creation_time = row["creation_time"]

        # ✅ `creation_time`이 `None`이면 현재 시간으로 대체 (또는 기본값 설정 가능)
        if creation_time is None:
            creation_time = datetime.utcnow()

        results.append(Result(
            result_id=row["result_id"],
            data=json.loads(row["data"]),  # ✅ JSON 문자열을 다시 Python 객체로 변환
            creation_time=creation_time
        ))

    return results