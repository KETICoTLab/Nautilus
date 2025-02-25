from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db_pool
from typing import List
from app.schemas.job import Job, JobCreate
from app.service import job as service

router = APIRouter(prefix="/projects/{project_id}/jobs", tags=["Jobs"])

@router.post("", response_model=Job)
async def create_job(project_id: str, data: JobCreate, pool=Depends(get_db_pool)):
    return await service.create_job(project_id, data, pool)

@router.get("/{job_id}", response_model=Job)
async def get_job(project_id: str, job_id: str, pool=Depends(get_db_pool)):
    job = await service.get_job(project_id, job_id, pool)
    if not job:
        raise HTTPException(status_code=404, detail="Job Not Found")
    return job

@router.patch("/{job_id}", response_model=Job)
async def update_job(project_id: str, job_id: str, data: JobCreate, pool=Depends(get_db_pool)):
    job = await service.update_job(project_id, job_id, data, pool)
    if not job:
        raise HTTPException(status_code=404, detail="Job Not Found")
    return job

@router.delete("/{job_id}")
async def delete_job(project_id: str, job_id: str, pool=Depends(get_db_pool)):
    success = await service.delete_job(project_id, job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job Not Found")
    return {"message": "Deleted successfully"}

@router.get("", response_model=List[Job])
async def list_jobs(project_id: str, pool=Depends(get_db_pool)):
    return await service.list_jobs(project_id)

@router.post("/{job_id}/exec")
async def exec_job(project_id: str, job_id: str):
    await service.exec_job(project_id, job_id)
    return {"message": f"Job {job_id} execution started for project {project_id}."}

@router.get("/{job_id}/client_status", response_model=Job)
async def get_client_status(project_id: str, job_id: str, pool=Depends(get_db_pool)):
    return await service.get_client_status(project_id, job_id)

@router.get("/{job_id}/job_status", response_model=Job)
async def get_job_status(project_id: str, job_id: str, pool=Depends(get_db_pool)):
    return await service.get_job_status(project_id, job_id)