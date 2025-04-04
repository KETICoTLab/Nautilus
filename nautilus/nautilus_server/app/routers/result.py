from fastapi import APIRouter, HTTPException, Depends, Request, Query
from app.database import get_db_pool
from typing import List, Optional
from app.schemas.result import Result, ResultCreate, ResultType
from app.service import result as service

router = APIRouter(prefix="/result", tags=["Result"])

@router.post("/{result_type}", response_model=Result)
async def create_result_by_type(
    result_type: ResultType,
    data: ResultCreate,
    request: Request,
    pool=Depends(get_db_pool)
):
    return await service.create_result(data, pool, request, result_type=result_type.value)

@router.get("/", response_model=List[Result])
async def get_result(
    type: Optional[str] = Query(None, description="Filter by result type"),
    pool=Depends(get_db_pool)
):
    return await service.get_result(pool, result_type=type)
