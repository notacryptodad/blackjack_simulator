import random
from ..base_strategy import BettingStrategy
from typing import List


class RandomBetStrategy(BettingStrategy):
    """Randomly selects bet amount within configured range"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.min_bet = config.get("min_bet", 5)
        self.max_bet = config.get("max_bet", 100)
    
    def get_bet(self, bankroll: float, history: List[dict]) -> float:
        max_allowed = min(self.max_bet, bankroll)
        if max_allowed < self.min_bet:
            return bankroll
        return random.uniform(self.min_bet, max_allowed)
    
    def reset(self):
        pass
