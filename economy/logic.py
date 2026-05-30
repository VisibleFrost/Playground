from random import randint, uniform, random
import math

RESOURCE_CONFIG = {
    "Electricity": {"base_value": 1.0, "mining_time_sec": 1.0, "is_liquid": True, "emission_per_mine": 100.0},
    "Oil": {"base_value": 5.0, "mining_time_sec": 5.0, "is_liquid": True, "emission_per_mine": 500.0},
    "Gold": {"base_value": 12.0, "mining_time_sec": 15.0, "is_liquid": False, "emission_per_mine": 1200.0},
    "Platinum": {"base_value": 17.0, "mining_time_sec": 22.0, "is_liquid": False, "emission_per_mine": 1700.0},
    "Uranium": {"base_value": 25.0, "mining_time_sec": 30.0, "is_liquid": False, "emission_per_mine": 2500.0}
}

class Economy:
    def __init__(self, user):
        self.currency_name = getattr(user, "currency_name", None)
        self.currency_value = float(getattr(user, "currency_value", 0.001))
        self.investor_trust = float(getattr(user, "investor_trust", 10.0))

        self.liquid_res_pool = {"Electricity": 0.0, "Oil": 0.0}
        self.reserved_res_pool = {"Gold": 0.0, "Platinum": 0.0, "Uranium": 0.0}
        self.printed_money = 0.0
        self.treasury_usd = 10.0
        
    def get_current_status_dict(self, log_message: str) -> dict:
        return {
            "status": "success",
            "message": log_message,
            "currency_name": self.currency_name,
            "currency_value": round(self.currency_value, 6),
            "investor_trust": round(self.investor_trust, 2),
            "liquid_pool": self.liquid_res_pool,
            "reserved_pool": self.reserved_res_pool,
            "printed_money": round(self.printed_money, 2),
            "treasury_usd": round(self.treasury_usd, 2)
        }

    def create_currency(self, name: str) -> dict:
        if self.currency_name:
            return {"status": "error", "message": "Национальная валюта уже объявлена!"}
        if not name or not name.strip():
            return {"status": "error", "message": "Имя валюты не может быть пустым!"}
        
        self.currency_name = name.strip()
        self.currency_value = 0.01
        self.investor_trust = 10.0
        return self.get_current_status_dict(f"Валюта {self.currency_name} успешно создана! Начальный курс: $0.01")

    def complete_mining(self, resource_name: str) -> dict:
        if not self.currency_name:
            return {"status": "error", "message": "Экономика не запущена. Сначала создайте государственную валюту!"}
            
        if resource_name not in RESOURCE_CONFIG:
            return {"status": "error", "message": "Неизвестный ресурс"}

        config = RESOURCE_CONFIG[resource_name]
        is_liquid = config["is_liquid"]
        emission = config["emission_per_mine"]

        if is_liquid:
            self.liquid_res_pool[resource_name] = self.liquid_res_pool.get(resource_name, 0.0) + 1.0
        else:
            self.reserved_res_pool[resource_name] = self.reserved_res_pool.get(resource_name, 0.0) + 1.0

        self.printed_money += emission

        total_liquid = sum(self.liquid_res_pool.values())
        total_reserved = sum(self.reserved_res_pool.values())
        total_resources = total_liquid + total_reserved

        current_count = self.liquid_res_pool.get(resource_name, 0) if is_liquid else self.reserved_res_pool.get(resource_name, 0)
        resource_ratio = current_count / total_resources if total_resources > 0 else 1.0

        msg = ""
        if total_resources > 3 and resource_ratio > 0.5:
            trust_penalty = round(uniform(1.5, 3.0), 2)
            self.investor_trust = max(0.0, self.investor_trust - trust_penalty)
            self.currency_value *= uniform(0.8, 0.9)
            msg = f"Майнинг {resource_name} завершен. Рынок перенасыщен одним ресурсом! Доверие упало на {trust_penalty}."
        else:
            trust_gain = round(uniform(2.0, 4.0), 2)
            self.investor_trust = min(100.0, self.investor_trust + trust_gain)
            self.currency_value *= uniform(1.05, 1.15)

            investor_investment = round((self.investor_trust * config["base_value"]) * 0.1, 2)
            self.treasury_usd += investor_investment
            msg = f"Успешный майнинг {resource_name}! Инвесторы оценили диверсификацию и вложили ${investor_investment}."

        if self.currency_value < 0.0001:
            self.currency_value = 0.0001

        return self.get_current_status_dict(msg)

    def simulate_market_tick(self) -> dict:
        return {"market_event": "Рынок стабилен. Ждет ваших действий."}