from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db_pool
from app.schemas.client import ClientCreate, ClientResponse, CheckStatusUpdate
from app.service import client as service

router = APIRouter(prefix="/projects/{project_id}/clients", tags=["Clients"])

@router.post("", response_model=ClientResponse)
async def register_client(project_id: str, client_data: ClientCreate, pool=Depends(get_db_pool)):
    return await service.create_client(project_id, client_data, pool)

@router.get("")
async def list_clients(project_id: str, name: str = None, pool=Depends(get_db_pool)):
    return await service.get_clients(project_id, name, pool)

@router.get("/{client_id}", response_model=ClientResponse)
async def retrieve_client(project_id: str, client_id: str, pool=Depends(get_db_pool)):
    client = service.get_client(project_id, client_id, pool)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return await client

@router.post("/{client_id}/check_status")
async def update_client_check_status(project_id: str, client_id: str, status_data: CheckStatusUpdate, pool=Depends(get_db_pool)):
    status = service.update_check_status(project_id, client_id, status_data, pool)
    if not status:
        raise HTTPException(status_code=404, detail="Check-status not found")
    return await status
