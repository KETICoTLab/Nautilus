from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ClientCreate(BaseModel):
    client_name: str
    data_id: str
    job_id: Optional[str] = None

class ClientResponse(ClientCreate):
    client_id: str
    job_id: Optional[str] = None
    project_id: str
    client_name: str
    data_id: str
    creation_time: datetime

class CheckStatusUpdate(BaseModel):
    validation_status: Optional[int] = None
    termination_status: Optional[int] = None
