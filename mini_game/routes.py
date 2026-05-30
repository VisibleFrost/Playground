from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import User, verify_password
from database import get_db
from .logic import GameState, get_status, process_attack, reset_game, get_log
from .models import BattleResponse, ActionRequest, LeaderboardUser

router = APIRouter(prefix="/mini_game", tags=["Mini_game"])

games = {}

def get_game(login: str, db: Session):
    if login not in games:
        user = db.query(User).filter(User.login == login).first()
        if user:
            games[login] = GameState(user)
    return games.get(login)

def save_game_to_db(login: str, game: GameState, db: Session):
    db.query(User).filter(User.login == login).update({
        "wins": game.wins,
        "hero_attack": game.hero_attack,
        "hero_buff": game.hero_buff
    })

def check_auth(login: str, password: str, db: Session):
    user = db.query(User).filter(User.login == login).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный логин или пароль")

@router.post("/status")
def status_endpoint(data: ActionRequest, db: Session = Depends(get_db)):
    check_auth(data.login, data.password, db)
    game = get_game(data.login, db)
    if not game:
        raise HTTPException(status_code=404, detail="Игра не найдена")
    return get_status(game)

@router.post("/attack", response_model=BattleResponse)
def attack(data: ActionRequest, db: Session = Depends(get_db)):
    check_auth(data.login, data.password, db)
    game = get_game(data.login, db)
    if not game:
        raise HTTPException(status_code=404, detail="Игра не найдена")
    
    result = process_attack(game)

    if result.enemy_dead:
        save_game_to_db(data.login, game, db)
        db.commit()

    return result

@router.post("/reset_profile")
def reset_profile(data: ActionRequest, db: Session = Depends(get_db)):
    check_auth(data.login, data.password, db)
    game = get_game(data.login, db)
    if not game:
        raise HTTPException(status_code=404, detail="Игра не найдена")
    
    result = reset_game(game)
    save_game_to_db(data.login, game, db)
    db.commit()
    return result

@router.post("/log")
def logs(data: ActionRequest, db: Session = Depends(get_db)):
    check_auth(data.login, data.password, db)
    game = get_game(data.login, db)
    if not game:
        raise HTTPException(status_code=404, detail="Игра не найдена")
    return {"log": get_log(game)}

@router.get("/leaderboard", response_model=List[LeaderboardUser])
def leaderboard(db: Session = Depends(get_db)):
    users = (
        db.query(User)
        .order_by(User.wins.desc())
        .limit(10)
        .all()
    )
    return users