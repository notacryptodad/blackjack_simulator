from typing import List, Dict


class SimulationResult:
    def __init__(self, starting_bankroll: float):
        self.starting_bankroll = starting_bankroll
        self.final_bankroll = 0
        self.hands_played = 0
        self.history: List[Dict] = []
        self.bankroll_history: List[float] = [starting_bankroll]
        
    @property
    def net_result(self) -> float:
        return self.final_bankroll - self.starting_bankroll
    
    @property
    def wins(self) -> int:
        return sum(1 for h in self.history if h['net_win'] > 0)
    
    @property
    def losses(self) -> int:
        return sum(1 for h in self.history if h['net_win'] < 0)
    
    @property
    def pushes(self) -> int:
        return sum(1 for h in self.history if h['net_win'] == 0)
    
    @property
    def win_rate(self) -> float:
        return self.wins / self.hands_played * 100 if self.hands_played > 0 else 0
    
    @property
    def total_wagered(self) -> float:
        return sum(h['bet'] for h in self.history)
    
    @property
    def ev_percent(self) -> float:
        return (sum(h['net_win'] for h in self.history) / self.total_wagered * 100) if self.total_wagered > 0 else 0
    
    @property
    def max_drawdown(self) -> float:
        peak = self.starting_bankroll
        max_dd = 0
        for balance in self.bankroll_history:
            if balance > peak:
                peak = balance
            drawdown = peak - balance
            if drawdown > max_dd:
                max_dd = drawdown
        return max_dd
    
    @property
    def peak_bankroll(self) -> float:
        return max(self.bankroll_history) if self.bankroll_history else self.starting_bankroll
    
    @property
    def max_bet(self) -> float:
        return max(h['bet'] for h in self.history) if self.history else 0
    
    @property
    def max_drawdown_percent(self) -> float:
        return (self.max_drawdown / self.starting_bankroll * 100) if self.starting_bankroll > 0 else 0
    
    def print_summary(self):
        print(f"\n{'='*50}")
        print(f"Simulation Complete")
        print(f"Starting bankroll: ${self.starting_bankroll:.2f}")
        print(f"Peak bankroll: ${self.peak_bankroll:.2f}")
        print(f"Final bankroll: ${self.final_bankroll:.2f}")
        print(f"Net result: ${self.net_result:+.2f}")
        print(f"Hands played: {self.hands_played}")
        print(f"Win rate: {self.win_rate:.1f}%")
        print(f"Wins: {self.wins} | Losses: {self.losses} | Pushes: {self.pushes}")
        print(f"Total wagered: ${self.total_wagered:.2f}")
        print(f"Max bet: ${self.max_bet:.2f}")
        print(f"Expected Value (EV): {self.ev_percent:+.2f}%")
        print(f"Max Drawdown: ${self.max_drawdown:.2f} ({self.max_drawdown_percent:.1f}%)")
    
    def export_to_csv(self, filename: str):
        """Export detailed hand history to CSV"""
        import csv
        with open(filename, 'w', newline='') as f:
            if not self.history:
                return
            writer = csv.DictWriter(f, fieldnames=self.history[0].keys())
            writer.writeheader()
            writer.writerows(self.history)


class SimulationRunner:
    def __init__(self, game_config = None, verbose: bool = False):
        self.game_config = game_config
        self.verbose = verbose
    
    def run(self, strategy, num_hands: int, starting_bankroll: float, 
            progress_interval: int = 100) -> SimulationResult:
        """Run a simulation session"""
        from engine import BlackjackGame
        
        game = BlackjackGame(self.game_config, verbose=self.verbose)
        result = SimulationResult(starting_bankroll)
        bankroll = starting_bankroll
        
        if not self.verbose:
            print(f"Running simulation: {num_hands} hands, starting bankroll ${starting_bankroll}\n")
        
        for hand_num in range(1, num_hands + 1):
            min_bet = self.game_config.min_bet if self.game_config else 5
            if bankroll < min_bet:
                print(f"\nInsufficient funds after {hand_num - 1} hands")
                break
            
            bet = strategy.get_bet(bankroll, result.history)
            game_result = game.play_hand(bet, strategy)
            bankroll += game_result.net_win
            
            result.history.append({
                "hand_num": hand_num,
                "bet": bet,
                "net_win": game_result.net_win,
                "outcome": game_result.outcome,
                "player_initial": game_result.initial_player_hand,
                "dealer_upcard": str(game_result.dealer_upcard),
                "dealer_final": str(game_result.dealer_hand),
                "player_final": [str(h) for h in game_result.player_hands],
                "actions": game_result.actions_taken,
                "bankroll_after": bankroll
            })
            result.bankroll_history.append(bankroll)
            
            if not self.verbose and progress_interval > 0 and hand_num % progress_interval == 0:
                print(f"Hand {hand_num}/{num_hands} - Bankroll: ${bankroll:.2f}")
        
        result.final_bankroll = bankroll
        result.hands_played = len(result.history)
        
        return result
