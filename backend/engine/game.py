from typing import List, Optional
from .card import Shoe, Card
from .hand import Hand


class GameConfig:
    def __init__(self, **kwargs):
        self.num_decks = kwargs.get("num_decks", 6)
        self.penetration = kwargs.get("penetration", 0.75)
        self.shuffle_every_hand = kwargs.get("shuffle_every_hand", False)
        self.dealer_hits_soft_17 = kwargs.get("dealer_hits_soft_17", False)
        self.dealer_peeks = kwargs.get("dealer_peeks", True)
        self.blackjack_payout = kwargs.get("blackjack_payout", 1.5)
        self.surrender_allowed = kwargs.get("surrender_allowed", True)
        self.double_after_split = kwargs.get("double_after_split", True)
        self.double_on = kwargs.get("double_on", "any")  # "any", "9-11", "10-11"
        self.resplit_aces = kwargs.get("resplit_aces", False)
        self.hit_split_aces = kwargs.get("hit_split_aces", False)
        self.max_hands = kwargs.get("max_hands", 4)
        self.min_bet = kwargs.get("min_bet", 5)
        self.max_bet = kwargs.get("max_bet", 500)


class GameResult:
    def __init__(self):
        self.player_hands = []
        self.dealer_hand = None
        self.net_win: float = 0
        self.outcome: str = ""  # "win", "loss", "push", "blackjack", "bust", "surrender"
        self.actions_taken = []  # List of actions player took
        self.dealer_upcard = None
        self.initial_player_hand = None


class BlackjackGame:
    def __init__(self, config: GameConfig = None, verbose: bool = True):
        self.config = config or GameConfig()
        self.shoe = Shoe(self.config.num_decks, self.config.penetration)
        self.dealer_hand: Optional[Hand] = None
        self.verbose = verbose
    
    def play_hand(self, bet: float, strategy) -> GameResult:
        """Play a single hand of blackjack"""
        result = GameResult()
        
        # Shuffle before each hand if configured
        if self.config.shuffle_every_hand:
            self.shoe.shuffle()
        
        # Initial deal
        player_hand = Hand()
        player_hand.bet = bet
        self.dealer_hand = Hand()
        
        player_hand.add_card(self.shoe.deal())
        self.dealer_hand.add_card(self.shoe.deal())
        player_hand.add_card(self.shoe.deal())
        dealer_upcard = self.shoe.deal()
        self.dealer_hand.add_card(dealer_upcard)
        
        result.dealer_upcard = dealer_upcard
        result.initial_player_hand = str(player_hand)
        
        if self.verbose:
            print(f"\n{'='*50}")
            print(f"Bet: ${bet}")
            print(f"Player: {player_hand}")
            print(f"Dealer: {dealer_upcard} ?")
        
        # Check for dealer blackjack
        if self.config.dealer_peeks and self.dealer_hand.is_blackjack():
            if self.verbose:
                print(f"Dealer has blackjack: {self.dealer_hand}")
            if player_hand.is_blackjack():
                result.outcome = "push"
                result.net_win = 0
                if self.verbose:
                    print("Push - both have blackjack")
            else:
                result.outcome = "loss"
                result.net_win = -bet
                if self.verbose:
                    print("Dealer blackjack - you lose")
            result.player_hands = [player_hand]
            result.dealer_hand = self.dealer_hand
            return result
        
        # Check for player blackjack
        if player_hand.is_blackjack():
            result.outcome = "blackjack"
            result.net_win = bet * self.config.blackjack_payout
            if self.verbose:
                print(f"Blackjack! You win ${result.net_win}")
            result.player_hands = [player_hand]
            result.dealer_hand = self.dealer_hand
            return result
        
        # Play player hand(s)
        hands = [player_hand]
        for hand in hands:
            if hand.is_surrendered:
                continue
            
            self._play_player_hand(hand, dealer_upcard, strategy, hands, result)
        
        # Play dealer hand
        if any(not h.is_busted() and not h.is_surrendered for h in hands):
            if self.verbose:
                print(f"\nDealer reveals: {self.dealer_hand}")
            while self._dealer_should_hit():
                card = self.shoe.deal()
                self.dealer_hand.add_card(card)
                if self.verbose:
                    print(f"Dealer hits: {card} -> {self.dealer_hand}")
            
            if self.dealer_hand.is_busted() and self.verbose:
                print("Dealer busts!")
        
        # Resolve all hands
        result.net_win = self._resolve_hands(hands)
        result.player_hands = hands
        result.dealer_hand = self.dealer_hand
        
        return result
    
    def _play_player_hand(self, hand: Hand, dealer_upcard: Card, strategy, all_hands: List[Hand], result: GameResult):
        """Play out a single player hand"""
        is_first_action = True
        
        while not hand.is_busted():
            game_state = {
                "can_double": is_first_action and self._can_double(hand),
                "can_split": is_first_action and hand.is_pair() and len(all_hands) < self.config.max_hands,
                "can_surrender": is_first_action and self.config.surrender_allowed and not hand.is_split_hand
            }
            
            action = strategy.get_action(hand, dealer_upcard, game_state)
            action_value = action.value if hasattr(action, 'value') else action
            result.actions_taken.append(action_value)
            
            if action_value == "stand":
                if self.verbose:
                    print("Stand")
                break
            
            elif action_value == "hit":
                card = self.shoe.deal()
                hand.add_card(card)
                if self.verbose:
                    print(f"Hit: {card} -> {hand}")
                if hand.is_busted() and self.verbose:
                    print("Bust!")
            
            elif action_value == "double":
                if game_state["can_double"]:
                    hand.bet *= 2
                    hand.is_doubled = True
                    card = self.shoe.deal()
                    hand.add_card(card)
                    if self.verbose:
                        print(f"Double down: {card} -> {hand}")
                    if hand.is_busted() and self.verbose:
                        print("Bust!")
                    break
                else:
                    if self.verbose:
                        print("Cannot double, hitting instead")
                    continue
            
            elif action_value == "split":
                if game_state["can_split"]:
                    if self.verbose:
                        print("Split!")
                    new_hand = Hand()
                    new_hand.bet = hand.bet
                    new_hand.is_split_hand = True
                    new_hand.add_card(hand.cards.pop())
                    hand.is_split_hand = True
                    
                    hand.add_card(self.shoe.deal())
                    new_hand.add_card(self.shoe.deal())
                    all_hands.append(new_hand)
                    
                    if self.verbose:
                        print(f"Hand 1: {hand}")
                        print(f"Hand 2: {new_hand}")
                else:
                    if self.verbose:
                        print("Cannot split, hitting instead")
                    continue
            
            elif action_value == "surrender":
                if game_state["can_surrender"]:
                    hand.is_surrendered = True
                    if self.verbose:
                        print("Surrender")
                    break
                else:
                    if self.verbose:
                        print("Cannot surrender, hitting instead")
                    continue
            
            is_first_action = False
    
    def _can_double(self, hand: Hand) -> bool:
        """Check if doubling is allowed"""
        if len(hand.cards) != 2:
            return False
        if hand.is_split_hand and not self.config.double_after_split:
            return False
        
        value = hand.value()
        if self.config.double_on == "10-11":
            return value in [10, 11]
        elif self.config.double_on == "9-11":
            return value in [9, 10, 11]
        return True
    
    def _dealer_should_hit(self) -> bool:
        """Determine if dealer should hit"""
        value = self.dealer_hand.value()
        if value < 17:
            return True
        if value == 17 and self.dealer_hand.is_soft() and self.config.dealer_hits_soft_17:
            return True
        return False
    
    def _resolve_hands(self, hands: List[Hand]) -> float:
        """Resolve all hands and return net win/loss"""
        net = 0
        dealer_value = self.dealer_hand.value()
        dealer_busted = self.dealer_hand.is_busted()
        
        for i, hand in enumerate(hands):
            if len(hands) > 1 and self.verbose:
                print(f"\nHand {i+1}: {hand}")
            
            if hand.is_surrendered:
                net -= hand.bet / 2
                if self.verbose:
                    print(f"Surrendered: lose ${hand.bet / 2}")
            elif hand.is_busted():
                net -= hand.bet
                if self.verbose:
                    print(f"Busted: lose ${hand.bet}")
            elif dealer_busted:
                net += hand.bet
                if self.verbose:
                    print(f"Dealer busted: win ${hand.bet}")
            else:
                player_value = hand.value()
                if player_value > dealer_value:
                    net += hand.bet
                    if self.verbose:
                        print(f"Win: ${hand.bet}")
                elif player_value < dealer_value:
                    net -= hand.bet
                    if self.verbose:
                        print(f"Lose: ${hand.bet}")
                else:
                    if self.verbose:
                        print("Push")
        
        if self.verbose:
            print(f"\nNet result: ${net:+.2f}")
        return net
