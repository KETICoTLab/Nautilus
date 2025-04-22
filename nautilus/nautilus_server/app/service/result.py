from typing import List, Optional
from app.service.base import fetch_one, fetch_all, execute
from app.schemas.result import ResultCreate, Result
from datetime import datetime, timezone, timedelta
KST = timezone(timedelta(hours=9))
import uuid
import json
from fastapi import Request
from collections import defaultdict


async def create_result(project_id, job_id, data, pool, request: Request, result_type: str):
    result_id = str(uuid.uuid4())[:8]

    # ✅ event_type과 data는 요청 객체에서 직접 사용
    event_type = data.event_type
    payload_data = data.data

    # ⏱ 포맷된 타임스탬프 생성
    now = datetime.now(KST)
    formatted_time = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

    # ✅ WebSocket 알림 전송용 메시지 구성
    message = json.dumps({
        "event": event_type,
        "result_id": result_id,
        "data": payload_data,
        "creation_time": formatted_time,
        "project_id": project_id,
        "job_id": job_id
    }, default=str)

    print(f"✅ WebSocket message: {message}")
    await request.app.websocket_manager.broadcast(message)

    # ⛔️ training_completed 이벤트는 DB에 저장하지 않음
    if event_type == "training_completed":
        return Result(
            result_id=result_id,
            data=payload_data,
            creation_time=formatted_time,
            project_id=project_id,
            job_id=job_id,
        )

    # ✅ 그 외 이벤트는 DB 저장
    query = """
    INSERT INTO results (result_id, data, creation_time, type, project_id, job_id)
    VALUES ($1, $2::jsonb, NOW(), $3, $4, $5)
    RETURNING *;
    """
    json_data = json.dumps(payload_data)
    row = await fetch_one(pool, query, result_id, json_data, result_type, project_id, job_id)

    creation_time = row["creation_time"].astimezone(KST)
    formatted_time = creation_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    return Result(
        result_id=row["result_id"],
        data=payload_data,
        creation_time=formatted_time,
        project_id=row["project_id"],
        job_id=row["job_id"],
    )

async def get_result(project_id, job_id, pool, result_type: Optional[str] = None):
    # ✅ 조건에 따라 쿼리 분기
    if result_type:
        query = """
        SELECT result_id, data, creation_time, project_id, job_id
        FROM results
        WHERE type = $1 AND project_id = $2 AND job_id = $3
        ORDER BY creation_time DESC;
        """
        rows = await fetch_all(pool, query, result_type, project_id, job_id)
    else:
        query = """
        SELECT result_id, data, creation_time, project_id, job_id
        FROM results
        WHERE project_id = $1 AND job_id = $2
        ORDER BY creation_time DESC;
        """
        rows = await fetch_all(pool, query, project_id, job_id)

    # ✅ 'client'인 경우 client_name 기준 200개 제한
    if result_type == "client":
        grouped = defaultdict(list)
        for row in rows:
            data = json.loads(row["data"])
            client_name = data.get("client_name", "unknown")
            if len(grouped[client_name]) < 200:
                creation_time = row["creation_time"] or datetime.utcnow()
                grouped[client_name].append(Result(
                    result_id=row["result_id"],
                    data=data,
                    creation_time=creation_time,
                    project_id=row["project_id"],
                    job_id=row["job_id"]
                ))
        results = [res for client_results in grouped.values() for res in client_results]

    # ✅ server는 모든 결과 반환
    else:
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