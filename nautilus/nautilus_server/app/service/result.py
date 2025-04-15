from typing import List, Optional
from app.service.base import fetch_one, fetch_all, execute
from app.schemas.result import ResultCreate, Result
from datetime import datetime, timezone, timedelta
KST = timezone(timedelta(hours=9))
import uuid
import json
from fastapi import Request

async def create_result(project_id, job_id, data, pool, request: Request, result_type: str):
    result_id = str(uuid.uuid4())[:8]

    query = """
    INSERT INTO results (result_id, data, creation_time, type, project_id, job_id)
    VALUES ($1, $2::jsonb, NOW(), $3, $4, $5)
    RETURNING *;
    """
    json_data = json.dumps(data.data)
    row = await fetch_one(pool, query, result_id, json_data, result_type, project_id, job_id)
    creation_time = row["creation_time"].astimezone(KST)
    formatted_time = creation_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    # ✅ WebSocket 알림 전송
    message = json.dumps({
        "event": f"{result_type}_result_created",
        "result_id": result_id,
        "data": json.loads(row["data"]),
        "timestamp": formatted_time,
        "project_id": project_id,
        "job_id": job_id
    }, default=str)
    print(f"✅ WebSocket message: {message}")
    await request.app.websocket_manager.broadcast(message)

    return Result(
        result_id=row["result_id"],
        data=json.loads(row["data"]),
        creation_time=formatted_time,
        project_id=row["project_id"],
        job_id=row["job_id"]
    )

async def get_result(project_id, job_id, pool, result_type: Optional[str] = None):
    # ✅ 조건에 따라 쿼리 분기
    if result_type:
        query = """
        SELECT result_id, data, creation_time, project_id, job_id
        FROM results
        WHERE type = $1 and project_id = $2 and job_id = $3
        ORDER BY creation_time DESC limit 10;
        """
        rows = await fetch_all(pool, query, result_type, project_id, job_id)
    else:
        query = """
        SELECT result_id, data, creation_time, project_id, job_id
        FROM results
        WHERE project_id = $1 and job_id = $2
        ORDER BY creation_time DESC limit 10;
        """
        rows = await fetch_all(pool, query, project_id, job_id)

    results = []
    for row in rows:
        creation_time = row["creation_time"] or datetime.utcnow()

        results.append(Result(
            result_id=row["result_id"],
            data=json.loads(row["data"]),
            creation_time=creation_time,
            project_id=row["project_id"],
            job_id=row["job_id"]
        ))

    return results