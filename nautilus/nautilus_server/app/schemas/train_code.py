from pydantic import BaseModel
from datetime import datetime

class TrainCodeBase(BaseModel):
    description: str
    creator_id: int
    code_file: bytes

class TrainCodeCreate(TrainCodeBase):
    pass

class TrainCode(TrainCodeBase):
    train_code_id: int
    project_id: int
    creation_time: datetime
    modification_time: datetime

    class Config:
        orm_mode = True
