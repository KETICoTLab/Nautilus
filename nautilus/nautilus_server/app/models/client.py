from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Client(Base):
    __tablename__ = "clients"

    client_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, nullable=False)
    client_name = Column(String, nullable=False)
    data_id = Column(String, nullable=False)
    job_id = Column(String, nullable=True)
    creation_time = Column(DateTime, default=func.now())

class CheckStatus(Base):
    __tablename__ = "check_status"

    check_status_id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.client_id"), nullable=False)
    job_id = Column(String, nullable=True)
    validation_status = Column(Integer, default=-1)  # -1: 연락없음
    termination_status = Column(Integer, default=-1)  # 0: 종료안됨, 1: 종료됨
    creation_time = Column(DateTime, default=func.now())
