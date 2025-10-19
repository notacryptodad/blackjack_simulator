#!/usr/bin/env python3
"""Demo script for random blackjack play"""

import sys
sys.path.insert(0, 'backend')

from engine import GameConfig
from strategies import Strategy
from strategies.betting.flat_bet import FlatBetStrategy
from strategies.playing.random_strategy import RandomStrategy
from simulator import SimulationRunner


def main():
    config = GameConfig(
        num_decks=6,
        dealer_hits_soft_17=False,
        blackjack_payout=1.5,
        surrender_allowed=True,
        double_after_split=True
    )
    
    betting = FlatBetStrategy({"bet_amount": 10})
    playing = RandomStrategy({})
    strategy = Strategy(betting, playing)
    
    runner = SimulationRunner(config, verbose=False)
    result = runner.run(
        strategy=strategy,
        num_hands=1000,
        starting_bankroll=1000,
        progress_interval=100
    )
    
    result.print_summary()
    print(f"\nNote: Random play typically has -10% to -20% EV")


if __name__ == "__main__":
    main()
