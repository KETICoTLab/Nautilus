from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ServiceBase(BaseModel):
    service_name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    creator_id: Optional[int] = None
    global_model_id: Optional[int] = None
    authorization: Optional[str] = None
    service_request_param: Optional[dict] = None
    service_response_info: Optional[dict] = None
    response_format_type: Optional[str] = None
    interface_type: Optional[str] = None
    error_info: Optional[str] = None

class ServiceCreate(ServiceBase):
    pass

class Service(ServiceBase):
    service_id: int
    project_id: int
    creation_time: datetime
    modification_time: datetime

    model_config = {
        "from_attributes": True,  # Pydantic v2에서는 `orm_mode = True` 대신 사용
        "arbitrary_types_allowed": True  # 사용자 정의 타입 허용
    }
