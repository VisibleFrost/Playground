from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import json
from database import User, verify_password
from database import get_db 
from .models import CreateCurrencyRequest, EconomyStatusRequest, MiningRequest
from .logic import Economy

router = APIRouter()

def get_and_auth_user(db: Session, login, password):
    user = db.query(User).filter(User.login == login).first()
    if not user:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный пароль")
    return user

def load_economy_state(user) -> Economy:
    eco = Economy(user)
    if hasattr(user, "economy_data_json") and user.economy_data_json:
        try:
            data = json.loads(user.economy_data_json)
            eco.liquid_res_pool = data.get("liquid", eco.liquid_res_pool)
            eco.reserved_res_pool = data.get("reserved", eco.reserved_res_pool)
            eco.printed_money = data.get("printed_money", eco.printed_money)
            eco.treasury_usd = data.get("treasury_usd", eco.treasury_usd)
        except Exception:
            pass
    return eco

def save_economy_state(user, eco: Economy):
    user.currency_name = eco.currency_name
    user.currency_value = eco.currency_value
    user.investor_trust = eco.investor_trust
    
    state_data = {
        "liquid": eco.liquid_res_pool,
        "reserved": eco.reserved_res_pool,
        "printed_money": eco.printed_money,
        "treasury_usd": eco.treasury_usd
    }
    user.economy_data_json = json.dumps(state_data)

@router.post("/create-currency")
def create_national_currency(data: CreateCurrencyRequest, db: Session = Depends(get_db)):
    user = get_and_auth_user(db, data.login, data.password)
    eco = load_economy_state(user)
    
    res = eco.create_currency(data.name)
    
    save_economy_state(user, eco)
    db.commit()
    return res

@router.post("/complete-mine")
def complete_mine(data: MiningRequest, db: Session = Depends(get_db)):
    user = get_and_auth_user(db, data.login, data.password)
    eco = load_economy_state(user)
    
    res = eco.complete_mining(data.resource_name)
    market_res = eco.simulate_market_tick()
    res["market_event"] = market_res.get("market_event")
    
    save_economy_state(user, eco)
    db.commit()
    return res

@router.post("/status")
def get_economy_status(data: EconomyStatusRequest, db: Session = Depends(get_db)):
    user = get_and_auth_user(db, data.login, data.password)
    eco = load_economy_state(user)

    return eco.get_current_status_dict("Текущий статус экономики.")

@router.get("/leaderboard")
def economy_leaderboard(db: Session = Depends(get_db)):
    users = (
        db.query(User)
        .filter(User.currency_name != None)
        .order_by(User.currency_value.desc())
        .limit(10)
        .all()
    )

    return [
        {
            "login": u.login,
            "currency_name": u.currency_name,
            "currency_value": u.currency_value
        }
        for u in users 
    ]