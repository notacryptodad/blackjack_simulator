#!/usr/bin/env python3
"""Demo script for manual blackjack play"""

import sys
sys.path.insert(0, 'backend')

from engine import BlackjackGame, GameConfig
from strategies import Strategy
from strategies.betting.flat_bet import FlatBetStrategy
from strategies.playing.manual import ManualStrategy


def main():
    config = GameConfig(
        num_decks=6,
        dealer_hits_soft_17=False,
        blackjack_payout=1.5,
        surrender_allowed=True,
        double_after_split=True
    )
    
    game = BlackjackGame(config, verbose=True)
    
    betting = FlatBetStrategy({"bet_amount": 10})
    playing = ManualStrategy({})
    strategy = Strategy(betting, playing)
    
    bankroll = 1000
    history = []
    
    print("Welcome to Blackjack!")
    print(f"Starting bankroll: ${bankroll}")
    print(f"Bet amount: $10")
    print("\nType 'quit' at any prompt to exit\n")
    
    while bankroll >= config.min_bet:
        try:
            bet = strategy.get_bet(bankroll, history)
            if bet > bankroll:
                print(f"\nInsufficient funds. Bankroll: ${bankroll}")
                break
            
            result = game.play_hand(bet, strategy)
            bankroll += result.net_win
            
            history.append({
                "bet": bet,
                "net_win": result.net_win,
                "outcome": result.outcome
            })
            
            print(f"\nBankroll: ${bankroll:.2f}")
            
            cont = input("\nPlay another hand? (y/n) [default: y]: ").lower().strip()
            if cont and cont != 'y':
                break
                
        except (KeyboardInterrupt, EOFError):
            break
    
    print(f"\n{'='*50}")
    print(f"Session ended")
    print(f"Final bankroll: ${bankroll:.2f}")
    print(f"Net result: ${bankroll - 1000:+.2f}")
    print(f"Hands played: {len(history)}")


if __name__ == "__main__":
    main()
