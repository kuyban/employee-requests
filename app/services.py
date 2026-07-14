from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime
from typing import List, Optional
from app.models import Request, Employee, StatusEnum

class RequestService:
    STATUS_TRANSITIONS = {
        StatusEnum.NEW: [StatusEnum.IN_PROGRESS],
        StatusEnum.IN_PROGRESS: [StatusEnum.COMPLETED],
        StatusEnum.COMPLETED: []
    }
    
    @staticmethod
    def can_transition(current_status: StatusEnum, new_status: StatusEnum) -> bool:
        if current_status == new_status:
            return True
        allowed = RequestService.STATUS_TRANSITIONS.get(current_status, [])
        return new_status in allowed
    
    @staticmethod
    def create_request(db: Session, number: str, author_id: int, executor_id: int, 
                      description: str, deadline: datetime) -> Request:
        author = db.query(Employee).filter(Employee.id == author_id).first()
        executor = db.query(Employee).filter(Employee.id == executor_id).first()
        
        if not author or not executor:
            raise ValueError("Author or executor could not be found")
        
        request = Request(
            number=number,
            author_id=author_id,
            executor_id=executor_id,
            description=description,
            deadline=deadline,
            status=StatusEnum.NEW
        )
        db.add(request)
        db.commit()
        db.refresh(request)
        return request
    
    @staticmethod
    def update_status(db: Session, request_id: int, new_status: StatusEnum) -> Request:
        request = db.query(Request).filter(Request.id == request_id).first()
        if not request:
            raise ValueError("Request not found")
        
        if not RequestService.can_transition(request.status, new_status):
            raise ValueError(
                f"Denied transition '{request.status.value}' into '{new_status.value}'"
            )
        
        request.status = new_status
        db.commit()
        db.refresh(request)
        return request
    
    @staticmethod
    def update_executor(db: Session, request_id: int, new_executor_id: int) -> Request:
        request = db.query(Request).filter(Request.id == request_id).first()
        if not request:
            raise ValueError("Request not found")
        
        executor = db.query(Employee).filter(Employee.id == new_executor_id).first()
        if not executor:
            raise ValueError("Executor not found")
        
        request.executor_id = new_executor_id
        db.commit()
        db.refresh(request)
        return request
    
    @staticmethod
    def get_requests(db: Session, status: Optional[StatusEnum] = None, 
                    executor_id: Optional[int] = None, department: Optional[str] = None,
                    overdue_only: bool = False) -> List[Request]:
        query = db.query(Request)
        
        if status:
            query = query.filter(Request.status == status)
        
        if executor_id:
            query = query.filter(Request.executor_id == executor_id)
        
        if department:
            query = query.join(Employee, Request.executor_id == Employee.id)\
                         .filter(Employee.department == department)
        
        if overdue_only:
            query = query.filter(
                and_(
                    Request.deadline < datetime.utcnow(),
                    Request.status != StatusEnum.COMPLETED
                )
            )
        
        return query.all()
    
    @staticmethod
    def get_overdue_in_progress_for_executor(db: Session, executor_id: int) -> List[Request]:
        return db.query(Request).filter(
            and_(
                Request.executor_id == executor_id,
                Request.status == StatusEnum.IN_PROGRESS,
                Request.deadline < datetime.utcnow()
            )
        ).order_by(Request.deadline).all()

class ReportService:
    @staticmethod
    def get_status_stats(db: Session) -> dict:
        result = db.query(
            Request.status,
            func.count(Request.id).label('count')
        ).group_by(Request.status).all()
        
        return {status.value: count for status, count in result}
    
    @staticmethod
    def get_overdue_count(db: Session) -> int:
        return db.query(Request).filter(
            and_(
                Request.deadline < datetime.utcnow(),
                Request.status != StatusEnum.COMPLETED
            )
        ).count()
    
    @staticmethod
    def get_completed_by_executor(db: Session) -> List[dict]:
        result = db.query(
            Employee.full_name,
            func.count(Request.id).label('completed_count')
        ).join(Request, Request.executor_id == Employee.id)\
         .filter(Request.status == StatusEnum.COMPLETED)\
         .group_by(Employee.id, Employee.full_name)\
         .order_by(func.count(Request.id).desc())\
         .all()
        
        return [{"executor": name, "completed_count": count} for name, count in result]