from typing import List
from .card import Card, Rank


class Hand:
    def __init__(self):
        self.cards: List[Card] = []
        self.bet: float = 0
        self.is_split_hand: bool = False
        self.is_doubled: bool = False
        self.is_surrendered: bool = False
    
    def add_card(self, card: Card):
        self.cards.append(card)
    
    def value(self) -> int:
        """Calculate best hand value (soft or hard)"""
        total = sum(card.rank.card_value for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == Rank.ACE)
        
        # Adjust for aces
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        
        return total
    
    def is_soft(self) -> bool:
        """Check if hand is soft (has ace counted as 11)"""
        total = sum(card.rank.card_value for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == Rank.ACE)
        return aces > 0 and total <= 21
    
    def is_busted(self) -> bool:
        return self.value() > 21
    
    def is_blackjack(self) -> bool:
        """Natural blackjack: Ace + 10-value card on initial 2 cards"""
        return (len(self.cards) == 2 and 
                self.value() == 21 and 
                not self.is_split_hand)
    
    def is_pair(self) -> bool:
        """Check if hand can be split"""
        if len(self.cards) != 2:
            return False
        return self.cards[0].rank.card_value == self.cards[1].rank.card_value
    
    def __str__(self):
        return f"{' '.join(str(c) for c in self.cards)} ({self.value()})"
