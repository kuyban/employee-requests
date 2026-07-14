from sqlalchemy.orm import Session
from app.models import Employee, Request, StatusEnum
from app.database import SessionLocal
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker('ru_RU')

def generate_employees(db: Session, count: int = 1000):
    departments = ['IT', 'HR', 'Finance', 'Sales', 'Marketing', 'Operations', 'R&D', 'Legal']
    positions = ['Manager', 'Senior Specialist', 'Specialist', 'Junior Specialist', 'Director', 'Assistant']
    
    employees = []
    for _ in range(count):
        employee = Employee(
            full_name=fake.name(),
            department=random.choice(departments),
            position=random.choice(positions)
        )
        employees.append(employee)
    
    db.add_all(employees)
    db.commit()
    print(f"Создано {count} сотрудников")
    return employees

def generate_requests(db: Session, count: int = 1000000, employees: list = None):
    if not employees:
        employees = db.query(Employee).all()
    
    if len(employees) < 2:
        raise ValueError("Нужно минимум 2 сотрудника")
    
    batch_size = 10000
    requests_batch = []
    
    for i in range(count):
        author = random.choice(employees)
        executor = random.choice([e for e in employees if e.id != author.id])
        
        status = random.choices(
            [StatusEnum.NEW, StatusEnum.IN_PROGRESS, StatusEnum.COMPLETED],
            weights=[0.2, 0.3, 0.5]
        )[0]
        
        created_date = fake.date_time_between(start_date='-365d', end_date='now')
        deadline = created_date + timedelta(days=random.randint(1, 30))
        
        request = Request(
            number=f"REQ-{datetime.now().strftime('%Y')}-{str(i+1).zfill(8)}",
            author_id=author.id,
            executor_id=executor.id,
            description=fake.text(max_nb_chars=200),
            created_date=created_date,
            deadline=deadline,
            status=status
        )
        
        requests_batch.append(request)
        
        if len(requests_batch) >= batch_size:
            db.add_all(requests_batch)
            db.commit()
            print(f"Создано {len(requests_batch)} заявок")
            requests_batch = []
    
    if requests_batch:
        db.add_all(requests_batch)
        db.commit()
        print(f"Создано {len(requests_batch)} заявок")
    
    print(f"Всего создано {count} заявок")

def main():
    db = SessionLocal()
    try:
        print("Начало генерации тестовых данных...")
        employees = generate_employees(db, 1000)
        generate_requests(db, 1000000, employees)
        print("Генерация данных завершена!")
    except Exception as e:
        print(f"Ошибка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()