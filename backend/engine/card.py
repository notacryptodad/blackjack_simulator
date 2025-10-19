from enum import Enum
from typing import List
import random


class Suit(Enum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"


class Rank(Enum):
    TWO = ("2", 2)
    THREE = ("3", 3)
    FOUR = ("4", 4)
    FIVE = ("5", 5)
    SIX = ("6", 6)
    SEVEN = ("7", 7)
    EIGHT = ("8", 8)
    NINE = ("9", 9)
    TEN = ("10", 10)
    JACK = ("J", 10)
    QUEEN = ("Q", 10)
    KING = ("K", 10)
    ACE = ("A", 11)
    
    def __init__(self, display, card_value):
        self.display = display
        self.card_value = card_value


class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit
    
    def __str__(self):
        return f"{self.rank.display}{self.suit.value}"
    
    def __repr__(self):
        return str(self)


class Shoe:
    def __init__(self, num_decks: int = 6, penetration: float = 0.75):
        self.num_decks = num_decks
        self.penetration = penetration
        self.cards: List[Card] = []
        self.shuffle()
    
    def shuffle(self):
        self.cards = []
        for _ in range(self.num_decks):
            for suit in Suit:
                for rank in Rank:
                    self.cards.append(Card(rank, suit))
        random.shuffle(self.cards)
        self.cut_card = int(len(self.cards) * self.penetration)
    
    def deal(self) -> Card:
        if len(self.cards) <= self.cut_card:
            self.shuffle()
        return self.cards.pop()
    
    def needs_shuffle(self) -> bool:
        return len(self.cards) <= self.cut_card
