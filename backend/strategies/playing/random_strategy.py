import random
from ..base_strategy import PlayingStrategy, Action


class RandomStrategy(PlayingStrategy):
    """Randomly selects from available actions"""
    
    def get_action(self, player_hand, dealer_upcard, game_state: dict) -> Action:
        available_actions = [Action.HIT, Action.STAND]
        
        if game_state.get("can_double", False):
            available_actions.append(Action.DOUBLE)
        if game_state.get("can_split", False):
            available_actions.append(Action.SPLIT)
        if game_state.get("can_surrender", False):
            available_actions.append(Action.SURRENDER)
        
        return random.choice(available_actions)
    
    def reset(self):
        pass
