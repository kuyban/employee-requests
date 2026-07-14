# 1. Клонировать проект

# 2. Запустить через Docker Compose (всё поднимется автоматически)
docker-compose up -d --build

# 3. Открыть в браузере
# http://localhost:8000/docs (Swagger для просмотра точек)

# http://localhost:8080 (Adminer - управление БД)

## Для Adminer
-Движок: PostgreSQL
-Сервер: db
-Имя пользователя: postgres
-Пароль: postgres
-База данныхм: emp_req

# 4. Сгенерировать тестовые данные
docker-compose exec app uv run python -m app.generate_data

# 4. Производительность для запроса
docker-compose exec app uv run python -m app.performance_test

# 5. Остановить
docker-compose down
