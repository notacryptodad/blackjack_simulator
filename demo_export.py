#!/usr/bin/env python3
"""Demo script showing detailed hand recording and export"""

import sys
sys.path.insert(0, 'backend')

from engine import GameConfig
from strategies import Strategy
from strategies.betting.flat_bet import FlatBetStrategy
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
    
    betting = FlatBetStrategy({"bet_amount": 10})
    playing = SmartStrategy({})
    strategy = Strategy(betting, playing)
    
    runner = SimulationRunner(config, verbose=False)
    result = runner.run(
        strategy=strategy,
        num_hands=100,
        starting_bankroll=1000,
        progress_interval=0  # No progress output
    )
    
    result.print_summary()
    
    # Show first 5 hands in detail
    print(f"\n{'='*50}")
    print("First 5 hands detail:")
    print(f"{'='*50}")
    for i, hand in enumerate(result.history[:5], 1):
        print(f"\nHand #{hand['hand_num']}:")
        print(f"  Player: {hand['player_initial']}")
        print(f"  Dealer: {hand['dealer_upcard']} ?")
        print(f"  Actions: {' -> '.join(hand['actions'])}")
        print(f"  Player final: {', '.join(hand['player_final'])}")
        print(f"  Dealer final: {hand['dealer_final']}")
        print(f"  Bet: ${hand['bet']:.2f} | Result: ${hand['net_win']:+.2f}")
        print(f"  Bankroll: ${hand['bankroll_after']:.2f}")
    
    # Export to CSV
    result.export_to_csv("simulation_results.csv")
    print(f"\n{'='*50}")
    print("Full hand history exported to: simulation_results.csv")
    print("You can now visualize bankroll trends, analyze decisions, etc.")


if __name__ == "__main__":
    main()
