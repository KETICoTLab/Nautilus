from fastapi import HTTPException
from typing import List, Optional
from app.schemas.job import JobCreate, Job
from app.database import pool
from app.service.base import fetch_one, fetch_all, execute
import subprocess
from pathlib import Path
import asyncio
#from app.config import HOST
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from nautilus.core.communicate.k8s import connect_get_namespaced_pod_exec  
from nautilus.core.communicate.docker import exec_command_in_container

async def create_job(project_id: str, data: JobCreate, pool) -> Job:
    job_id = "j-kr-" + data.job_name
    query = """
    INSERT INTO jobs (project_id, job_id, job_name, description, tags, creator_id, creation_time, modification_time, job_status, client_status, aggr_function, admin_info, data_id, global_model_id, contri_est_method, num_global_iteration, num_local_epoch, job_config)
    VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW(), $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
    RETURNING *;
    """
    HOST = "172.17.0.1" #컨테이너에서 로컬로 통신
    cmd_str = (
        f'cd /workspace/nautilus/nautilus/api && '
        f'python3 run_export_job.py '
        f'--contribution_method {data.contri_est_method} '
        f'--server_url {HOST} '
        f'--n_clients {len(data.data_id)} '
        f'--num_rounds {data.num_global_iteration} '
        f'--num_local_epoch {data.num_local_epoch} '
        f'--job_name {job_id}'
        f'--project_id {project_id}'
    )

    print(f"🟢 Running command string: {cmd_str}")

    try:
        #connect_get_namespaced_pod_exec(pod_name="mylocalhost", command=cmd_str)
        exec_command_in_container(container_name="mylocalhost", command=cmd_str)

    except Exception as e:
        print(f"❌ create_job failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    # 🔹 Step 3: DB에 Job 정보 저장
    row = await fetch_one(
        pool, query, project_id, job_id, data.job_name, data.description, data.tags, data.creator_id,
        data.job_status, data.client_status, data.aggr_function, data.admin_info, data.data_id,
        data.global_model_id, data.contri_est_method, data.num_global_iteration, data.num_local_epoch, data.job_config
    )
    
    return Job(**row)


async def get_job(project_id: str, job_id: str, pool) -> Optional[Job]:
    query = "SELECT * FROM jobs WHERE job_id = $1;"
    row = await fetch_one(pool, query, job_id)
    return Job(**row) if row else None

async def update_job(project_id: str, job_id: str, data: JobCreate) -> Optional[Job]:
    query = """
    UPDATE jobs
    SET job_name = $1, description = $2, tags = $3, creator_id = $4, host_information = $5, train_code_path = $6, train_data_path = $7, modification_time = NOW()
    WHERE job_id = $8
    RETURNING *;
    """
    row = await fetch_one(pool, query, data.job_name, data.description, data.tags, data.creator_id, data.host_information, data.train_code_path, data.train_data_path, job_id)
    return Job(**row) if row else None

async def delete_job(project_id: str, job_id: str, pool) -> bool:
    query = "DELETE FROM jobs WHERE job_id = $1;"
    result = await execute(pool, query, job_id)
    return result.endswith("DELETE 1")

async def list_jobs(project_id, pool) -> List[Job]:
    query = "SELECT * FROM jobs;"
    rows = await fetch_all(pool, query)
    return [Job(**row) for row in rows]

async def exec_job(project_id: str, job_id: str):
    """execute_job.py 실행"""
    
    #execute_job_script = Path("../nautilus/api/run/run_execute_job.py").resolve()  # nautilus/ 디렉토리에 위치
    execute_job_script = Path("../nautilus/api/run/run_execute_job_container.py").resolve()
    
    execute_job_command = [
        "python3", str(execute_job_script),
        "--project_id", project_id,
        "--job_id", job_id
    ]
    
    print(f"Running execute_job.py: {' '.join(execute_job_command)}")
    try:
        # * 실시간 로그 출력하도록 변경
        process = subprocess.Popen(
            execute_job_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # * 문자열로 변환하여 실시간 출력
        )

        # * 표준 출력 및 오류 로그 실시간 출력
        for line in process.stdout:
            print(f"[exec_job.py LOG]: {line.strip()}")

        for line in process.stderr:
            print(f"[exec_job.py ERROR]: {line.strip()}")

        process.wait()  # * 프로세스 종료까지 대기
        print(f"* exec_job.py finished with exit code {process.returncode}")

    except Exception as e:
        print(f"* exec_job failed: {e}")

async def get_client_status(project_id: str, job_id: str, pool) -> Optional[Job]:
    query = """
    """

    row = await fetch_one(pool, query, project_id, job_id)
    return Job(**row)

async def get_job_status(project_id: str, job_id: str, pool) -> Optional[Job]:
    query = """
    """

    row = await fetch_one(pool, query, project_id, job_id)
    return Job(**row)