from pydantic import BaseModel, Field, computed_field
from typing import Optional

class ActionRequest(BaseModel):
    login: str
    password: str

class BattleResponse(BaseModel):
    damage: int
    enemy_hp_left: int
    enemy_dead: bool
    loot: Optional[str] = None
    log: str

class LeaderboardUser(BaseModel):
    login: str
    wins: int
    hero_attack: int = Field(exclude=True)
    hero_buff: int = Field(exclude=True)

    @computed_field
    def hero_damage(self) -> int:
        return self.hero_attack + self.hero_buff