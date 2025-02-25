
from pydantic import BaseModel
from typing import Optional, List, Dict

class HostInformation(BaseModel):
    ip_address: str  # IP 주소
    username: str  # 계정 이름
    password: str  # 계정 비밀번호

class DataProviderBase(BaseModel):
    data_provider_name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    creator_id: Optional[int] = None
    host_information: HostInformation
    train_code_path: str
    train_data_path: str

class DataProviderCreate(DataProviderBase):
    pass

class DataProvider(DataProviderBase):
    data_provider_id: str

    model_config = {
        "from_attributes": True,  # Pydantic v2에서는 `orm_mode = True` 대신 사용
        "arbitrary_types_allowed": True  # 사용자 정의 타입 허용
    }
 
        
class DataProviderDataBase(BaseModel):
    item_code_id: str
    data_name: str
    description: str
    data: Optional[str] = None

class DataProviderDataCreate(DataProviderDataBase):
    pass

class DataProviderData(DataProviderDataBase):
    data_id: str

    model_config = {
        "from_attributes": True,  # Pydantic v2에서는 `orm_mode = True` 대신 사용
        "arbitrary_types_allowed": True  # 사용자 정의 타입 허용
    }

