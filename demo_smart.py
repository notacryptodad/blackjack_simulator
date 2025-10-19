#!/usr/bin/env python3
"""Demo script for smart (basic strategy) blackjack play"""

import sys
sys.path.insert(0, 'backend')

from engine import GameConfig
from strategies import Strategy
from strategies.betting.flat_bet import FlatBetStrategy
from strategies.playing.smart import SmartStrategy
from simulator import SimulationRunner


def main():
    # Setup game
    config = GameConfig(
        num_decks=6,
        dealer_hits_soft_17=False,
        blackjack_payout=1.5,
        surrender_allowed=True,
        double_after_split=True
    )
    
    # Setup strategy
    betting = FlatBetStrategy({"bet_amount": 10})
    playing = SmartStrategy({})
    strategy = Strategy(betting, playing)
    
    # Run simulation
    runner = SimulationRunner(config, verbose=False)
    result = runner.run(
        strategy=strategy,
        num_hands=1000,
        starting_bankroll=1000,
        progress_interval=100
    )
    
    # Print results
    result.print_summary()
    print(f"\nNote: Basic strategy EV should be around -0.5% for these rules")


if __name__ == "__main__":
    main()
