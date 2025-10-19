#!/usr/bin/env python3
"""Compare simulation with and without shuffling every hand"""

import sys
sys.path.insert(0, 'backend')

from engine import GameConfig
from strategies import Strategy
from strategies.betting.flat_bet import FlatBetStrategy
from strategies.playing.smart import SmartStrategy
from simulator import SimulationRunner


def main():
    betting = FlatBetStrategy({"bet_amount": 10})
    playing = SmartStrategy({})
    strategy = Strategy(betting, playing)
    
    # Standard penetration (75%)
    print("=" * 60)
    print("STANDARD: Shuffle at 75% penetration (realistic casino)")
    print("=" * 60)
    config_standard = GameConfig(
        num_decks=6,
        penetration=0.75,
        shuffle_every_hand=False,
        dealer_hits_soft_17=False,
        blackjack_payout=1.5,
        surrender_allowed=True,
        double_after_split=True
    )
    
    runner = SimulationRunner(config_standard, verbose=False)
    result_standard = runner.run(strategy, 1000, 1000, progress_interval=0)
    result_standard.print_summary()
    
    # Shuffle every hand (CSM simulation)
    print("\n" + "=" * 60)
    print("CSM MODE: Shuffle every hand (card counting useless)")
    print("=" * 60)
    config_csm = GameConfig(
        num_decks=6,
        shuffle_every_hand=True,
        dealer_hits_soft_17=False,
        blackjack_payout=1.5,
        surrender_allowed=True,
        double_after_split=True
    )
    
    runner_csm = SimulationRunner(config_csm, verbose=False)
    result_csm = runner_csm.run(strategy, 1000, 1000, progress_interval=0)
    result_csm.print_summary()
    
    # Comparison
    print("\n" + "=" * 60)
    print("COMPARISON")
    print("=" * 60)
    print(f"Standard EV: {result_standard.ev_percent:+.2f}%")
    print(f"CSM EV:      {result_csm.ev_percent:+.2f}%")
    print(f"Difference:  {result_standard.ev_percent - result_csm.ev_percent:+.2f}%")
    print("\nNote: With basic strategy (no counting), results should be similar.")
    print("Card counting strategies would show significant difference.")


if __name__ == "__main__":
    main()
