from ..base_strategy import BettingStrategy
from typing import List


class MartingaleStrategy(BettingStrategy):
    """Double bet after each loss, reset to base bet after win"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.base_bet = config.get("base_bet", 10)
        self.max_bet = config.get("max_bet", 500)
        self.current_bet = self.base_bet
    
    def get_bet(self, bankroll: float, history: List[dict]) -> float:
        # First hand or after a win
        if not history or history[-1]['net_win'] >= 0:
            self.current_bet = self.base_bet
        else:
            # After a loss, double the bet
            self.current_bet = min(self.current_bet * 2, self.max_bet)
        
        # Don't bet more than bankroll
        return min(self.current_bet, bankroll)
    
    def reset(self):
        self.current_bet = self.base_bet
