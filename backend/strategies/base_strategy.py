from abc import ABC, abstractmethod
from enum import Enum
from typing import List


class Action(Enum):
    HIT = "hit"
    STAND = "stand"
    DOUBLE = "double"
    SPLIT = "split"
    SURRENDER = "surrender"


class BettingStrategy(ABC):
    def __init__(self, config: dict):
        self.config = config
    
    @abstractmethod
    def get_bet(self, bankroll: float, history: List[dict]) -> float:
        """Determine bet amount based on bankroll and hand history"""
        pass
    
    @abstractmethod
    def reset(self):
        """Reset strategy state for new session"""
        pass


class PlayingStrategy(ABC):
    def __init__(self, config: dict):
        self.config = config
    
    @abstractmethod
    def get_action(self, player_hand, dealer_upcard, game_state: dict) -> Action:
        """
        Determine action based on player hand, dealer upcard, and game state
        
        game_state includes:
        - can_double: bool
        - can_split: bool
        - can_surrender: bool
        """
        pass
    
    @abstractmethod
    def reset(self):
        """Reset strategy state for new session"""
        pass


class Strategy:
    """Aggregates betting and playing strategies"""
    def __init__(self, betting: BettingStrategy, playing: PlayingStrategy):
        self.betting = betting
        self.playing = playing
    
    def get_bet(self, bankroll: float, history: List[dict]) -> float:
        return self.betting.get_bet(bankroll, history)
    
    def get_action(self, player_hand, dealer_upcard, game_state: dict) -> Action:
        return self.playing.get_action(player_hand, dealer_upcard, game_state)
    
    def reset(self):
        self.betting.reset()
        self.playing.reset()
