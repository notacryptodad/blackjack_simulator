from ..base_strategy import PlayingStrategy, Action


class SmartStrategy(PlayingStrategy):
    """Basic strategy for infinite decks (dealer stands on soft 17)"""
    
    def get_action(self, player_hand, dealer_upcard, game_state: dict) -> Action:
        player_value = player_hand.value()
        is_soft = player_hand.is_soft()
        is_pair = player_hand.is_pair()
        dealer_value = dealer_upcard.rank.card_value
        
        # Adjust dealer ace to 11 for lookup
        if dealer_upcard.rank.display == "A":
            dealer_value = 11
        
        # Pair splitting logic
        if is_pair and game_state.get("can_split", False):
            card_value = player_hand.cards[0].rank.card_value
            if card_value == 11:  # A,A
                return Action.SPLIT
            elif card_value == 10:  # 10,10
                return Action.STAND
            elif card_value == 9:  # 9,9
                if dealer_value in [7, 10, 11]:
                    return Action.STAND
                return Action.SPLIT
            elif card_value == 8:  # 8,8
                return Action.SPLIT
            elif card_value == 7:  # 7,7
                if dealer_value <= 7:
                    return Action.SPLIT
                return Action.HIT
            elif card_value == 6:  # 6,6
                if dealer_value <= 6:
                    return Action.SPLIT
                return Action.HIT
            elif card_value == 5:  # 5,5
                if dealer_value <= 9:
                    return Action.DOUBLE if game_state.get("can_double", False) else Action.HIT
                return Action.HIT
            elif card_value == 4:  # 4,4
                if dealer_value in [5, 6]:
                    return Action.SPLIT
                return Action.HIT
            elif card_value in [2, 3]:  # 2,2 or 3,3
                if dealer_value <= 7:
                    return Action.SPLIT
                return Action.HIT
        
        # Soft hand logic
        if is_soft and player_value <= 21:
            if player_value >= 19:  # A,8 or A,9
                return Action.STAND
            elif player_value == 18:  # A,7
                if dealer_value <= 6:
                    return Action.DOUBLE if game_state.get("can_double", False) else Action.STAND
                elif dealer_value in [7, 8]:
                    return Action.STAND
                else:
                    return Action.HIT
            elif player_value == 17:  # A,6
                if dealer_value <= 6:
                    return Action.DOUBLE if game_state.get("can_double", False) else Action.HIT
                return Action.HIT
            elif player_value in [15, 16]:  # A,4 or A,5
                if dealer_value in [4, 5, 6]:
                    return Action.DOUBLE if game_state.get("can_double", False) else Action.HIT
                return Action.HIT
            elif player_value in [13, 14]:  # A,2 or A,3
                if dealer_value in [5, 6]:
                    return Action.DOUBLE if game_state.get("can_double", False) else Action.HIT
                return Action.HIT
        
        # Hard hand logic
        if player_value >= 17:
            return Action.STAND
        elif player_value == 16:
            if dealer_value >= 9 and game_state.get("can_surrender", False):
                return Action.SURRENDER
            if dealer_value <= 6:
                return Action.STAND
            return Action.HIT
        elif player_value == 15:
            if dealer_value == 10 and game_state.get("can_surrender", False):
                return Action.SURRENDER
            if dealer_value <= 6:
                return Action.STAND
            return Action.HIT
        elif player_value in [13, 14]:
            if dealer_value <= 6:
                return Action.STAND
            return Action.HIT
        elif player_value == 12:
            if dealer_value in [4, 5, 6]:
                return Action.STAND
            return Action.HIT
        elif player_value == 11:
            return Action.DOUBLE if game_state.get("can_double", False) else Action.HIT
        elif player_value == 10:
            if dealer_value <= 9:
                return Action.DOUBLE if game_state.get("can_double", False) else Action.HIT
            return Action.HIT
        elif player_value == 9:
            if dealer_value in [3, 4, 5, 6]:
                return Action.DOUBLE if game_state.get("can_double", False) else Action.HIT
            return Action.HIT
        else:  # 4-8
            return Action.HIT
    
    def reset(self):
        pass
