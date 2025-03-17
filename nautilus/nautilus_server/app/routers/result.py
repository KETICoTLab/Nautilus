from fastapi import APIRouter, HTTPException, Depends
from app.database import get_db_pool
from typing import List
from app.schemas.result import Result, ResultCreate
from app.service import result as service

router = APIRouter(prefix="/result", tags=["Result"])

@router.post("/", response_model=Result)
async def create_result(data: ResultCreate, pool=Depends(get_db_pool)):
    return await service.create_result(data, pool)

@router.get("/", response_model=List[Result])
async def get_result(pool=Depends(get_db_pool)):
    return await service.get_result(pool)
