from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.job import Job

class ProjectBase(BaseModel):
    project_name: str 
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    creator_id: Optional[str] = None
    data_provider_ids: Optional[List[str]] = None
    number_of_clients: int
    number_of_jobs: int = 0
    number_of_subscriptions: int = 0
    project_image: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    project_id: str
    creation_time: datetime
    modification_time: datetime
    jobs: List[Job] = [] 

    model_config = {
        "from_attributes": True,  # Pydantic v2에서는 `orm_mode = True` 대신 사용
        "arbitrary_types_allowed": True  # 사용자 정의 타입 허용
    }

