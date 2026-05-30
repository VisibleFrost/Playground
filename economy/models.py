from pydantic import BaseModel
from typing import Optional, Dict, Any

class CreateCurrencyRequest(BaseModel):
    login: str
    password: str
    name: str

class EconomyStatusRequest(BaseModel):
    login: str
    password: str

class MiningRequest(BaseModel):
    login: str
    password: str
    resource_name: str

class EconomyStatusResponse(BaseModel):
    status: str
    message: str
    currency_name: Optional[str] = None
    currency_value: float
    investor_trust: float
    liquid_pool: Dict[str, Any]
    reserved_pool: Dict[str, Any]
    printed_money: float = 0.0
    treasury_usd: float = 0.0