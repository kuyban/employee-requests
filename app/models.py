from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Index, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class StatusEnum(str, enum.Enum):
    NEW = "Новая"
    IN_PROGRESS = "В работе"
    COMPLETED = "Выполнена"

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False, index=True)
    department = Column(String(100), nullable=False, index=True)
    position = Column(String(100), nullable=False)
    
    created_requests = relationship("Request", foreign_keys="Request.author_id", back_populates="author")
    assigned_requests = relationship("Request", foreign_keys="Request.executor_id", back_populates="executor")

class Request(Base):
    __tablename__ = "requests"
    
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(50), nullable=False, unique=True, index=True)
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow(), index=True)
    description = Column(Text, nullable=False)
    deadline = Column(DateTime, nullable=False, index=True)
    status = Column(Enum(StatusEnum), nullable=False, default=StatusEnum.NEW, index=True)
    
    author_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    executor_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    author = relationship("Employee", foreign_keys=[author_id], back_populates="created_requests")
    executor = relationship("Employee", foreign_keys=[executor_id], back_populates="assigned_requests")
    
    __table_args__ = (
        Index('idx_requests_executor_status_deadline', 'executor_id', 'status', 'deadline'),
        Index('idx_requests_status_created', 'status', 'created_date'),
        Index('idx_requests_department_status', 'executor_id', 'status'),
    )