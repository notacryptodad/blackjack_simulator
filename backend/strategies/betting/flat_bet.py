from ..base_strategy import BettingStrategy
from typing import List


class FlatBetStrategy(BettingStrategy):
    """Fixed bet amount every hand"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.bet_amount = config.get("bet_amount", 10)
    
    def get_bet(self, bankroll: float, history: List[dict]) -> float:
        return min(self.bet_amount, bankroll)
    
    def reset(self):
        pass
