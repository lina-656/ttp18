# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Создаем приложение FastAPI
app = FastAPI()

# Определяем модель ответа на ошибки
class ErrorResponseModel(BaseModel):
    status_code: int
    message: str
    error_code: str

# Определяем пользовательские классы исключений
class UserNotFoundException(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id

class InvalidUserDataException(Exception):
    def __init__(self, message: str):
        self.message = message

# Регистрация пользовательских обработчиков исключений
@app.exception_handler(UserNotFoundException)
async def user_not_found_exception_handler(request, exc: UserNotFoundException):
    return ErrorResponseModel(
        status_code=404,
        message=f"User with ID {exc.user_id} not found.",
        error_code="USER_NOT_FOUND"
    )

@app.exception_handler(InvalidUserDataException)
async def invalid_user_data_exception_handler(request, exc: InvalidUserDataException):
    return ErrorResponseModel(
        status_code=400,
        message=exc.message,
        error_code="INVALID_USER_DATA"
    )

# Пользовательская модель для регистрации
class User(BaseModel):
    username: str
    email: str

# Временное хранилище пользователей
fake_user_db = {}

# Конечная точка для регистрации пользователя
@app.post("/register/")
async def register_user(user: User):
    if user.username in fake_user_db:
        raise InvalidUserDataException("User already exists.")
    
    fake_user_db[user.username] = user
    return {"message": "User registered successfully."}

# Конечная точка для получения пользовательских данных
@app.get("/user/{username}")
async def get_user(username: str):
    if username not in fake_user_db:
        raise UserNotFoundException(user_id=username)
    
    return fake_user_db[username]

# Мы также можем добавить заголовок для времени, если необходимо
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds()
    response.headers["X-ErrorHandleTime"] = str(process_time)
    return response

# Запуск приложения с uvicorn
# uvicorn main:app --reload
