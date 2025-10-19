#!/usr/bin/env python3
"""Demo script for Martingale betting strategy"""

import sys
sys.path.insert(0, 'backend')

from engine import GameConfig
from strategies import Strategy
from strategies.betting.martingale import MartingaleStrategy
from strategies.playing.smart import SmartStrategy
from simulator import SimulationRunner


def main():
    config = GameConfig(
        num_decks=6,
        dealer_hits_soft_17=False,
        blackjack_payout=1.5,
        surrender_allowed=True,
        double_after_split=True
    )
    
    betting = MartingaleStrategy({"base_bet": 1, "max_bet": 500})
    playing = SmartStrategy({})
    strategy = Strategy(betting, playing)
    
    runner = SimulationRunner(config, verbose=False)
    result = runner.run(
        strategy=strategy,
        num_hands=1000,
        starting_bankroll=1000,
        progress_interval=100
    )
    
    result.print_summary()
    
    # Show betting pattern
    print(f"\n{'='*50}")
    print("Betting pattern (first 20 hands):")
    for i, hand in enumerate(result.history[:20], 1):
        outcome = "WIN" if hand['net_win'] > 0 else "LOSS" if hand['net_win'] < 0 else "PUSH"
        print(f"Hand {i:2d}: Bet ${hand['bet']:6.2f} -> {outcome:4s} ${hand['net_win']:+7.2f} (Bankroll: ${hand['bankroll_after']:.2f})")
    
    print(f"\nNote: Martingale doubles bet after loss, resets after win")
    print(f"Warning: High risk of ruin with long losing streaks!")


if __name__ == "__main__":
    main()
