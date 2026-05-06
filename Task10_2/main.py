from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, conint, constr, ValidationError
from typing import Optional
import re

class User(BaseModel):
    username: str
    age: conint(gt=18)
    email: EmailStr
    password: constr(min_length=8, max_length=16)
    phone: Optional[str] = '8-800-555-35-35'

class ValidationErrorResponse(BaseModel):
    status_code: int
    message: str
    errors: list[dict]

app = FastAPI()

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    errors = []
    for error in exc.errors():
        field = error["loc"][-1] 
        msg = error["msg"]
        errors.append({
            "field": field,
            "message": msg
        })
    
    return JSONResponse(
        status_code=422,
        content=ValidationErrorResponse(
            status_code=422,
            message="Ошибка валидации данных",
            errors=errors
        ).model_dump()
    )

@app.post("/register")
async def register_user(user: User):
    return {
        "message": f"Пользователь '{user.username}' успешно зарегистрирован",
        "data": {
            "username": user.username,
            "age": user.age,
            "email": user.email,
            "phone": user.phone
        }
    }