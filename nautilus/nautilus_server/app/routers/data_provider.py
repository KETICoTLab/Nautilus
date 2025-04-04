from fastapi import APIRouter, HTTPException, Depends
from app.database import get_db_pool
from typing import List
from app.schemas.data_provider import DataProvider, DataProviderCreate, DataProviderData, DataProviderDataCreate, DataProviderDataResponse
from app.service import data_provider as service

router = APIRouter(prefix="/data-providers", tags=["Data Providers"])

@router.post("", response_model=DataProvider)
async def create_data_provider(data: DataProviderCreate, pool=Depends(get_db_pool)):
    return await service.create_data_provider(data, pool)

@router.get("/{data_provider_id}", response_model=DataProvider)
async def get_data_provider(data_provider_id: str, pool=Depends(get_db_pool)):
    dp = await service.get_data_provider(data_provider_id, pool)
    if not dp:
        raise HTTPException(status_code=404, detail="Data Provider Not Found")
    return dp

@router.patch("/{data_provider_id}", response_model=DataProvider)
async def update_data_provider(data_provider_id: str, data: DataProviderCreate, pool=Depends(get_db_pool)):
    dp = await service.update_data_provider(data_provider_id, data, pool)
    if not dp:
        raise HTTPException(status_code=404, detail="Data Provider Not Found")
    return dp

@router.delete("/{data_provider_id}")
async def delete_data_provider(data_provider_id: str, pool=Depends(get_db_pool)):
    success = await service.delete_data_provider(data_provider_id, pool)
    if not success:
        raise HTTPException(status_code=404, detail="Data Provider Not Found")
    return {"detail": "Deleted successfully"}

@router.get("", response_model=List[DataProviderData])
async def list_data_providers(pool=Depends(get_db_pool)):
    return await service.list_data_provider_data_all(pool)

@router.post("/{data_provider_id}/datas", response_model=DataProviderData)
async def create_data_provider_data(data_provider_id: str, data: DataProviderDataCreate, pool=Depends(get_db_pool)):
    return await service.create_data_provider_data(data_provider_id, data, pool)

@router.get("/{data_provider_id}/datas", response_model=List[DataProviderDataResponse])
async def list_data_provider_data(data_provider_id: str, pool=Depends(get_db_pool)):
    return await service.list_data_provider_data(data_provider_id, pool)

@router.delete("/{data_provider_id}/datas/{data_id}")
async def delete_data_provider_data(data_provider_id: str, data_id: str, pool=Depends(get_db_pool)):
    success = await service.delete_data_provider_data(data_provider_id, data_id, pool)
    if not success:
        raise HTTPException(status_code=404, detail="Data Provider Not Found")
    return {"detail": "Deleted successfully"}