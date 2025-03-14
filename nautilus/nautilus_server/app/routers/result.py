from fastapi import APIRouter, HTTPException, Depends
from app.database import get_db_pool
from typing import List
from app.service import result as service

router = APIRouter(prefix="/result")

@router.post("")
async def create_result(data, pool=Depends(get_db_pool)):
    return await service.create_result(data, pool)

@router.get("")
async def list_result():
    return await service.list_result()

