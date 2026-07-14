from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.models import StatusEnum, Base, Employee
from app.services import RequestService, ReportService
from app.database import get_db, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Система управления заявками")

class EmployeeCreate(BaseModel):
    full_name: str
    department: str
    position: str

class RequestCreate(BaseModel):
    number: str
    author_id: int
    executor_id: int
    description: str
    deadline: datetime

class RequestUpdateStatus(BaseModel):
    status: StatusEnum

class RequestUpdateExecutor(BaseModel):
    executor_id: int

class RequestResponse(BaseModel):
    id: int
    number: str
    created_date: datetime
    description: str
    deadline: datetime
    status: StatusEnum
    author_id: int
    executor_id: int
    
    class Config:
        from_attributes = True

# Эндпоинты для сотрудников
@app.post("/employees/")
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@app.get("/employees/")
def get_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()

# Эндпоинты для заявок
@app.post("/requests/", response_model=RequestResponse)
def create_request(request: RequestCreate, db: Session = Depends(get_db)):
    try:
        return RequestService.create_request(
            db,
            request.number,
            request.author_id,
            request.executor_id,
            request.description,
            request.deadline
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/requests/{request_id}/status", response_model=RequestResponse)
def update_request_status(
    request_id: int,
    status_update: RequestUpdateStatus,
    db: Session = Depends(get_db)
):
    try:
        return RequestService.update_status(db, request_id, status_update.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/requests/{request_id}/executor", response_model=RequestResponse)
def update_request_executor(
    request_id: int,
    executor_update: RequestUpdateExecutor,
    db: Session = Depends(get_db)
):
    try:
        return RequestService.update_executor(db, request_id, executor_update.executor_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/requests/", response_model=List[RequestResponse])
def get_requests(
    status: Optional[StatusEnum] = None,
    executor_id: Optional[int] = None,
    department: Optional[str] = None,
    overdue_only: bool = False,
    db: Session = Depends(get_db)
):
    return RequestService.get_requests(db, status, executor_id, department, overdue_only)

@app.get("/requests/executor/{executor_id}/overdue-in-progress")
def get_overdue_in_progress(
    executor_id: int,
    db: Session = Depends(get_db)
):
    return RequestService.get_overdue_in_progress_for_executor(db, executor_id)

# Эндпоинты для отчетов
@app.get("/reports/status-stats")
def get_status_stats(db: Session = Depends(get_db)):
    return ReportService.get_status_stats(db)

@app.get("/reports/overdue-count")
def get_overdue_count(db: Session = Depends(get_db)):
    return {"overdue_count": ReportService.get_overdue_count(db)}

@app.get("/reports/completed-by-executor")
def get_completed_by_executor(db: Session = Depends(get_db)):
    return ReportService.get_completed_by_executor(db)

@app.get("/")
def read_root():
    return {
        "message": "Система управления заявками",
        "docs": "/docs"
    }