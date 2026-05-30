from random import randint
import math
from .models import BattleResponse

class GameState:
    def __init__(self, user):
        self.user_login = user.login
        self.hero_attack = user.hero_attack
        self.hero_buff = user.hero_buff
        self.enemy_hp = 5
        self.enemy_hp_max = 5
        self.wins = user.wins
        self.last_bonus_wins = 0
        self.battle_log = []

def get_status(game: GameState):
    return {
        "hero_damage": game.hero_attack + game.hero_buff,
        "hero_buff": game.hero_buff,
        "enemy_hp": game.enemy_hp,
        "enemy_hp_max": game.enemy_hp_max,
        "wins": game.wins
    }

def process_attack(game: GameState) -> BattleResponse:
    total_damage = game.hero_attack + game.hero_buff
    game.enemy_hp -= total_damage
    log_message = f"Нанесен урон {total_damage}."

    loot = None
    enemy_dead = False

    if game.enemy_hp <= 0:
        game.enemy_hp = 0
        game.wins += 1
        enemy_dead = True
        log_message += " Враг повержен."

        if randint(1, 100) <= 15:
            loot = "атака +1"

            if loot == "атака +1":
                game.hero_buff += 1
                log_message += f" Получен {loot}! Атака увеличена."

        base_hp = 5 + int(game.wins * 0.8)

        if randint(1, 100) <= 15:
            elite_multiplier = randint(2, 4)
            game.enemy_hp_max = int(base_hp * elite_multiplier)
            log_message += f" ЭЛИТНЫЙ враг с x{elite_multiplier} HP! (вместо {base_hp})."
        else:
            game.enemy_hp_max = base_hp
            log_message += f" Обычный враг с {game.enemy_hp_max} HP."
    
        game.enemy_hp = game.enemy_hp_max

    if game.wins % 25 == 0 and game.wins > 0 and game.wins != game.last_bonus_wins:
        bonus = int(math.log2(game.wins // 10 + 1))
        game.hero_attack += bonus
        game.last_bonus_wins = game.wins
        log_message += f" За 25 побед +{bonus} к атаке!"

    game.battle_log.append(log_message)

    return BattleResponse(
        damage=total_damage,
        enemy_hp_left=max(0, game.enemy_hp),
        enemy_dead=enemy_dead,
        loot=loot,
        log=log_message
    )

def reset_game(game: GameState):
    game.hero_attack = 1
    game.hero_buff = 0
    game.enemy_hp_max = 5
    game.enemy_hp = game.enemy_hp_max
    game.wins = 0
    game.battle_log = []
    return {"message": "Игра сброшена"}

def get_log(game: GameState):
    return {"log": game.battle_log[-10:]}