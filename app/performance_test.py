from sqlalchemy import text
from app.database import SessionLocal
import time

def test_performance(executor_id: int):
    db = SessionLocal()
    try:
        db.execute(text("DROP INDEX IF EXISTS idx_requests_executor_status_deadline"))
        db.commit()

        print("Выполнение запроса...")
        start_time = time.time()
        
        query = text("""
            EXPLAIN (ANALYZE, BUFFERS)
            SELECT * FROM requests 
            WHERE executor_id = :executor_id 
            AND status = 'IN_PROGRESS' 
            AND deadline < NOW()
            ORDER BY deadline
        """)
        
        result = db.execute(query, {"executor_id": executor_id})
        execution_time = time.time() - start_time
        
        print(f"Время выполнения: {execution_time:.4f} секунд")
        print("\nПлан выполнения:")
        for row in result:
            print(row[0])
        
        return execution_time
    finally:
        db.close()

def test_optimized_performance(executor_id: int):
    db = SessionLocal()

    try:

        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_requests_executor_status_deadline 
            ON requests (executor_id, status, deadline)
        """))
        db.commit()

        print("\nВыполнение запроса с оптимизацией...")
        start_time = time.time()
        
        query = text("""
            EXPLAIN (ANALYZE, BUFFERS)
            SELECT * FROM requests 
            WHERE executor_id = :executor_id 
            AND status = 'IN_PROGRESS' 
            AND deadline < NOW()
            ORDER BY deadline
        """)
        
        result = db.execute(query, {"executor_id": executor_id})
        execution_time = time.time() - start_time
        
        print(f"Время выполнения: {execution_time:.4f} секунд")
        print("\nПлан выполнения:")
        for row in result:
            print(row[0])
        
        return execution_time
    finally:
        db.close()

if __name__ == "__main__":
    executor_id = 1
    
    print("ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ")
    
    time_before = test_performance(executor_id)
    time_after = test_optimized_performance(executor_id)
    
    print("РЕЗУЛЬТАТЫ СРАВНЕНИЯ")
    print(f"До оптимизации: {time_before:.4f} сек")
    print(f"После оптимизации: {time_after:.4f} сек")
    print(f"Ускорение: {(time_before / time_after):.2f}x")