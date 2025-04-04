from typing import List, Optional
from app.service.base import fetch_one, fetch_all, execute
from app.schemas.result import ResultCreate, Result
from datetime import datetime, timezone, timedelta
KST = timezone(timedelta(hours=9))
import uuid
import json
from fastapi import Request

async def create_result(data, pool, request: Request, result_type: str):
    result_id = str(uuid.uuid4())[:8]

    query = """
    INSERT INTO results (result_id, data, creation_time, type)
    VALUES ($1, $2::jsonb, NOW(), $3)
    RETURNING *;
    """
    json_data = json.dumps(data.data)
    row = await fetch_one(pool, query, result_id, json_data, result_type)
    creation_time = row["creation_time"].astimezone(KST)
    formatted_time = creation_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    # ✅ WebSocket 알림 전송
    message = json.dumps({
        "event": f"{result_type}_result_created",
        "result_id": result_id,
        "data": json.loads(row["data"]),
        "timestamp": formatted_time
    }, default=str)
    print(f"✅ WebSocket message: {message}")
    await request.app.websocket_manager.broadcast(message)

    return Result(
        result_id=row["result_id"],
        data=json.loads(row["data"]),
        creation_time=formatted_time
    )

async def get_result(pool, result_type: Optional[str] = None):
    # ✅ 조건에 따라 쿼리 분기
    if result_type:
        query = """
        SELECT result_id, data, creation_time
        FROM results
        WHERE type = $1
        ORDER BY creation_time DESC limit 10;
        """
        rows = await fetch_all(pool, query, result_type)
    else:
        query = """
        SELECT result_id, data, creation_time
        FROM results
        ORDER BY creation_time DESC limit 10;
        """
        rows = await fetch_all(pool, query)

    results = []
    for row in rows:
        creation_time = row["creation_time"] or datetime.utcnow()

        results.append(Result(
            result_id=row["result_id"],
            data=json.loads(row["data"]),
            creation_time=creation_time
        ))

    return results