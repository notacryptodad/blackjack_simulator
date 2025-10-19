from ..base_strategy import PlayingStrategy, Action


class ManualStrategy(PlayingStrategy):
    """Manual strategy that prompts user for each action"""
    
    def get_action(self, player_hand, dealer_upcard, game_state: dict) -> Action:
        print(f"\nYour hand: {player_hand}")
        print(f"Dealer shows: {dealer_upcard}")
        
        available_actions = ["hit", "stand"]
        
        if game_state.get("can_double", False):
            available_actions.append("double")
        if game_state.get("can_split", False):
            available_actions.append("split")
        if game_state.get("can_surrender", False):
            available_actions.append("surrender")
        
        while True:
            action_str = input(f"Choose action {available_actions} [default: {available_actions[0]}]: ").lower().strip()
            if not action_str:
                return Action(available_actions[0])
            if action_str in available_actions:
                return Action(action_str)
            print(f"Invalid action. Choose from {available_actions}")
    
    def reset(self):
        pass
