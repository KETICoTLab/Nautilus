from pydantic import BaseModel
from datetime import datetime

class GlobalModelBase(BaseModel):
    global_model_name: str
    parent_model_id: int
    final_performance_factor: float
    train_start_time: datetime
    train_end_time: datetime
    model_file: bytes

class GlobalModelCreate(GlobalModelBase):
    pass

class GlobalModel(GlobalModelBase):
    global_model_id: int
    project_id: int

    model_config = {
        "from_attributes": True,  # Pydantic v2에서는 `orm_mode = True` 대신 사용
        "arbitrary_types_allowed": True  # 사용자 정의 타입 허용
    }

