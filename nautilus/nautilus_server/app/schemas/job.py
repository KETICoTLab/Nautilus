from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class JobBase(BaseModel):
    nvflare_job_id: Optional[str] = None
    job_name: str
    description: Optional[str] = None
    tags: Optional[str] = None
    creator_id: Optional[str] = None
    job_status: Optional[str] = None
    client_status: Optional[str] = None
    aggr_function: str
    admin_info: str
    data_id: List[str]
    global_model_id: Optional[str] = None
    train_code_id: Optional[str] = None
    contri_est_method: Optional[str] = None
    num_global_iteration: Optional[int] = 1
    num_local_epoch: Optional[int] = 1
    job_config: Optional[str] = None

class JobCreate(JobBase):
    pass

class Job(JobBase):
    job_id: str
    project_id: str
    nvflare_job_id: Optional[str] = None
    data_id: List[str]
    creation_time: datetime
    
    model_config = {
        "from_attributes": True,  # Pydantic v2에서는 `orm_mode = True` 대신 사용
        "arbitrary_types_allowed": True  # 사용자 정의 타입 허용
    }
