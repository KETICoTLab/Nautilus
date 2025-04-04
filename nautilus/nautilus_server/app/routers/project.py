from fastapi import APIRouter, HTTPException, Depends
from app.database import get_db_pool
from typing import List
from app.schemas.project import Project, ProjectCreate
from app.service import project as service

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("", response_model=Project)
async def create_project(data: ProjectCreate, pool=Depends(get_db_pool)):
    return await service.create_project(data, pool)

@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str, pool=Depends(get_db_pool)):
    proj = await service.get_project(project_id, pool)
    if not proj:
        raise HTTPException(status_code=404, detail="Project Not Found")
    return proj

@router.patch("/{project_id}", response_model=Project)
async def update_project(project_id: str, data: ProjectCreate, pool=Depends(get_db_pool)):
    proj = await service.update_project(project_id, data, pool)
    if not proj:
        raise HTTPException(status_code=404, detail="Project Not Found")
    return proj

@router.delete("/{project_id}")
async def delete_project(project_id: str, pool=Depends(get_db_pool)):
    success = await service.delete_project(project_id, pool)
    if not success:
        raise HTTPException(status_code=404, detail="Project Not Found")
    return {"detail": "Deleted successfully"}

@router.get("", response_model=List[Project])
async def list_projects(pool=Depends(get_db_pool)):
    return await service.list_projects(pool)

@router.post("/{project_id}/validation_check")
async def validation_check(project_id: str, pool=Depends(get_db_pool)):
    return await service.validation_check(project_id, pool)

@router.get("/{project_id}/client-status")
async def get_status(project_id: str, pool=Depends(get_db_pool)):
    result = await service.get_client_status(project_id, pool)
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to fetch client status")
    return {"project_id": project_id, "clients": result}