from typing import List, Optional
from app.schemas.job import JobCreate, Job
from app.database import pool
from app.service.base import fetch_one, fetch_all, execute
import subprocess
from pathlib import Path
import asyncio

async def create_job(project_id: str, data: JobCreate, pool) -> Job:
    job_id = "J-KR-" + data.job_name
    query = """
    INSERT INTO jobs (project_id, job_id, job_name, description, tags, creator_id, creation_time, modification_time, job_status, client_status, aggr_function, admin_info, data_id, global_model_id, contri_est_method, num_global_iteration, num_local_epoch, job_config)
    VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW(), $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
    RETURNING *;
    """
    
    '''
    # run_create_job.py 실행 
    create_job_script = "../nautilus/api/run/run_create_job.py"  # nautilus/ 디렉토리에 위치 
    create_job_command = [
        "python3", create_job_script,
        "--config_path", f"{project_id}_config.json",
        "--job_id", job_id,
        "--aggr_function", data.aggr_function,
        "--num_global_iteration", str(data.num_global_iteration),
        "--num_local_epoch", str(data.num_local_epoch)
    ]
    '''
    
    # ✅ export_job.py 실행 (simulation version)
    create_job_script = Path("../nautilus/api/contrib/export_job.py").resolve()  # 절대 경로 변환
    create_job_command = ["python3", str(create_job_script)]
    
    # ✅ run_deploy_job.py 실행 
    deploy_job_script = Path("../nautilus/api/run/run_deploy_job.py").resolve()  # 절대 경로 변환
    deploy_job_command = [
        "python3", str(deploy_job_script),
        "--config_path", f"{project_id}_config.json",
        "--job_id", job_id
    ]

    print(f"🟢 Running create_job_script: {create_job_command}")

    try:
        # 🔹 Step 1: create_job 실행
        create_process = await asyncio.create_subprocess_exec(
            *create_job_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout, stderr = await create_process.communicate()

        print(f"[create_job.py LOG]: {stdout.decode().strip()}")
        print(f"[create_job.py ERROR]: {stderr.decode().strip()}")

        if create_process.returncode != 0:
            print(f"❌ create_job.py failed with exit code {create_process.returncode}")
            return None  # 실패 시 중단

        print(f"✅ create_job.py finished successfully.")

        # 🔹 Step 2: deploy_job 실행 (create_job 성공 후 실행)
        print(f"🟢 Running deploy_job_script: {deploy_job_command}")
        deploy_process = await asyncio.create_subprocess_exec(
            *deploy_job_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout, stderr = await deploy_process.communicate()

        print(f"[deploy_job.py LOG]: {stdout.decode().strip()}")
        print(f"[deploy_job.py ERROR]: {stderr.decode().strip()}")

        if deploy_process.returncode != 0:
            print(f"❌ deploy_job.py failed with exit code {deploy_process.returncode}")
            return None  # 실패 시 중단

        print(f"✅ deploy_job.py finished successfully.")

    except Exception as e:
        print(f"❌ create_job failed: {e}")
        return None  # 실패 시 중단

    # 🔹 Step 3: DB에 Job 정보 저장
    row = await fetch_one(
        pool, query, project_id, job_id, data.job_name, data.description, data.tags, data.creator_id,
        data.job_status, data.client_status, data.aggr_function, data.admin_info, data.data_id,
        data.global_model_id, data.contri_est_method, data.num_global_iteration, data.num_local_epoch, data.job_config
    )
    
    return Job(**row)


async def get_job(project_id: str, job_id: str) -> Optional[Job]:
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

async def delete_job(project_id: str, job_id: str) -> bool:
    query = "DELETE FROM jobs WHERE job_id = $1;"
    result = await execute(pool, query, job_id)
    return result.endswith("DELETE 1")

async def list_jobs() -> List[Job]:
    query = "SELECT * FROM jobs;"
    rows = await fetch_all(pool, query)
    return [Job(**row) for row in rows]

async def exec_job(project_id: str, job_id: str):
    """execute_job.py 실행"""
    
    execute_job_script = Path("../nautilus/api/run/run_execute_job.py").resolve()  # nautilus/ 디렉토리에 위치
    '''
    execute_job_command = [
        "python3", str(execute_job_script),
        "--project_id", project_id,
        "--job_id", job_id
    ]
    '''
    execute_job_command = [
        "python3", str(execute_job_script),
        "--project_id", project_id,
        "--job_id", "hello-pt_cifar10_fedavg"
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
            print(f"[create_job.py LOG]: {line.strip()}")

        for line in process.stderr:
            print(f"[create_job.py ERROR]: {line.strip()}")

        process.wait()  # * 프로세스 종료까지 대기
        print(f"* create_job.py finished with exit code {process.returncode}")

    except Exception as e:
        print(f"* create_job failed: {e}")

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