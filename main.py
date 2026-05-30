import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional
from database import SessionLocal, User, hash_password, verify_password, get_db
from mini_game.routes import router as minigame_router
from maze import router as maze_router
from economy.routes import router as economy_router
from converter import router as converter_router
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session

logging.basicConfig(
    filename='backend_errors.log', 
    level=logging.ERROR, 
    format='%(asctime)s -- %(levelname)s -- %(message)s'
)

tags_metadata = [
    {"name": "Auth", "description": "Регистрация и авторизация"},
    {"name": "Mini_game", "description": "Мини-игра с битвами"},
    {"name": "Maze", "description": "Лабиринт"},
    {"name": "Economy", "description": "Криптобиржа и национальные валюты"},
    {"name": "Converter", "description": "Кастомный конвертер систем счисления"}
]

app = FastAPI(openapi_tags=tags_metadata, docs_url=None, redoc_url=None)

app.include_router(minigame_router)
app.include_router(maze_router)
app.include_router(economy_router, prefix="/economy", tags=["Economy"])
app.include_router(converter_router)

class RegisterRequest(BaseModel):
    login: str
    password: str

@app.post("/register", tags=["Auth"])
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.login == data.login).first()
    if existing:
        raise HTTPException(status_code=400, detail="Логин занят")
    
    hashed = hash_password(data.password)

    new_user = User(
        login=data.login,
        hashed_password=hashed,
        wins=0,
        hero_attack=1,
        hero_buff=0
    )
    db.add(new_user)
    db.commit()

    return {"ok": True, "message": f"Пользователь {data.login} создан"}

@app.post("/login", tags=["Auth"])
def login(data: RegisterRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.login == data.login).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Пользователь не найден")

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный пароль")

    return {"ok": True, "message": "Успешный вход", "login": user.login}

@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = Path(__file__).parent / "index.html"
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Критическая ошибка при запросе к {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Внутренняя ошибка сервера", "details": str(exc)}
    )