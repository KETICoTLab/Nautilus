from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from datetime import datetime
from enum import Enum

class ResultCreate(BaseModel):
    """JSON 데이터를 필드 없이 그대로 받을 수 있도록 설정"""
    event_type: Optional[str] = None
    data: Dict[str, Any] = Field(..., description="임의의 JSON 데이터를 저장")  # ✅ JSON 전체를 받음

    class Config:
        from_attributes = True  # ✅ Pydantic v2에서 `orm_mode` 대체
        arbitrary_types_allowed = True  # ✅ 모든 데이터 타입을 허용
        
class Result(ResultCreate):
    result_id: str  # 데이터베이스에서 ID를 관리하는 경우 추가
    creation_time: datetime  # 생성 시간을 저장
    project_id: str
    job_id: str

    model_config = {
        "from_attributes": True,  # Pydantic v2에서 `orm_mode = True` 대신 사용
        "arbitrary_types_allowed": True  # 사용자 정의 타입 허용
    }
    
class ResultType(str, Enum):
    server = "server"
    client = "client"

class ResultResponse(BaseModel):
    result_id: str  # 데이터베이스에서 ID를 관리하는 경우 추가
    creation_time: datetime  # 생성 시간을 저장
    project_id: str
    job_id: str
    data: Dict[str, Any] = Field(..., description="임의의 JSON 데이터를 저장")  # ✅ JSON 전체를 받음

    model_config = {
        "from_attributes": True,  # Pydantic v2에서 `orm_mode = True` 대신 사용
        "arbitrary_types_allowed": True  # 사용자 정의 타입 허용
    }