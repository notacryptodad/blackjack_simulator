# Blackjack Strategy Testing Engine - Design Document

## Overview
A modular blackjack simulation engine that allows testing different betting strategies with statistical analysis and visualization.

## Blackjack Game Rules

### Objective
**Beat the dealer** - not just get close to 21. Player must first not bust, then either outscore the dealer or have the dealer bust.

### Card Values
- Number cards (2-10): Face value
- Face cards (J, Q, K): 10 points
- Ace: 1 or 11 points (player's choice)

### Gameplay Flow

**1. Initial Setup**
- 1 to 8 decks of 52-card decks (default: 6)
- Shuffle when penetration reaches 75% (configurable)
- Minimum and maximum bet limits

**2. Betting Phase**
- Player places bet before cards are dealt
- Bet must be within table limits

**3. Dealing**
- Player receives 2 cards face up
- Dealer receives 2 cards: 1 face up (upcard), 1 face down (hole card)

**4. Insurance (Optional Side Bet)**
- Offered only when dealer shows Ace
- Pays 2:1 if dealer has blackjack
- Wager up to half of original bet
- Resolved immediately after dealer checks hole card

**5. Dealer Blackjack Check**
- If dealer shows Ace or 10-value card, dealer peeks at hole card
- If dealer has blackjack (Ace + 10-value card):
  - All player bets lose immediately (except insurance)
  - If player also has blackjack: push (tie, bet returned)
  - Round ends, no player actions taken

**6. Player Blackjack**
- If player has blackjack and dealer does not: pays 3:2 immediately (configurable)
- Blackjack beats all 21-point hands that are not blackjack
- Round ends, no further actions

**7. Player Actions** (if no natural blackjack)
- **Stand**: Keep current hand, no more cards
- **Hit**: Take another card (can repeat). If total exceeds 21, player busts and loses immediately
- **Double Down**: Double the bet, receive exactly one more card, then must stand
  - Allowed on any first two cards (configurable: can restrict to 9-11 or 10-11 only)
  - Allowed after split (configurable)
- **Split**: If two cards have same rank (or both 10-value), split into two separate hands
  - Place equal bet on second hand
  - Each hand played independently from left to right
  - Can resplit up to 3 times (4 hands total) (configurable: can restrict to 2-3 hands)
  - Aces can be resplit (configurable: default false)
  - Split Aces receive only one card each (configurable: default true)
  - Ace + 10 after split counts as 21, not blackjack (pays 1:1)
- **Surrender**: Forfeit half the bet, keep other half, hand ends immediately
  - Late surrender only (after dealer checks for blackjack) (configurable)
  - Only available as first action on initial two cards
  - Not available after split or hit

**8. Dealer Play**
- Dealer reveals hole card after all players complete their hands
- Dealer must hit on 16 or less (hard or soft)
- Dealer must stand on hard 17 or higher
- Dealer hits soft 17 (Ace-6) (configurable: default false for most casinos)
- Dealer has no choices - rules are automatic

**9. Hand Resolution**
- Player busts (>21): Loses bet (already resolved during player's turn)
- Dealer busts (>21): All remaining players win 1:1
- Dealer higher than player: Player loses bet
- Player higher than dealer: Player wins 1:1
- Equal totals: Push (bet returned, no win/loss)
- Player blackjack: 3:2 (configurable: some tables pay 6:5 or even money - avoid these)

### Hand Evaluation Rules
- **Hard Hand**: No Ace, or Ace counted as 1 (to avoid busting)
- **Soft Hand**: Ace counted as 11 without busting (e.g., Ace-6 = soft 17)
- **Bust**: Hand value exceeds 21
- **Blackjack**: Ace + 10-value card on initial two cards only (not after split)

### Rule Variations Impact on House Edge
Based on standard 8-deck, dealer stands on soft 17, double after split allowed:

**Player-Favorable Rules:**
- Single deck: +0.48%
- Double deck: +0.19%
- Player may draw to split aces: +0.19%
- Player may resplit aces: +0.08%
- Late surrender: +0.08%

**House-Favorable Rules:**
- Dealer hits soft 17: -0.22%
- No double after split: -0.14%
- European no hole card: -0.11%
- Double on 10-11 only: -0.18%
- Double on 9-11 only: -0.09%
- Blackjack pays 6:5: -1.39% (AVOID)
- Blackjack pays even money: -2.27% (AVOID)

### Configurable Game Parameters
```python
game_config = {
    # Deck Configuration
    "num_decks": 6,              # 1-8 decks (1, 2, 4, 6, 8 common)
    "penetration": 0.75,         # Reshuffle at 75% of shoe
    
    # Dealer Rules
    "dealer_hits_soft_17": False,  # True = dealer hits soft 17
    "dealer_peeks": True,          # Dealer checks for blackjack with A or 10
    
    # Payouts
    "blackjack_payout": 1.5,     # 3:2 = 1.5, 6:5 = 1.2, even = 1.0
    
    # Player Options
    "surrender_allowed": True,   # Late surrender only
    "insurance_allowed": True,   # Insurance side bet when dealer shows Ace
    
    # Doubling Rules
    "double_after_split": True,  # Can double after splitting
    "double_on": "any",          # "any", "9-11", or "10-11"
    
    # Splitting Rules
    "resplit_aces": False,       # Can resplit Aces
    "hit_split_aces": False,     # Can hit split Aces (usually false)
    "max_hands": 4,              # Max hands after splitting (2-4)
    
    # Table Limits
    "min_bet": 5,
    "max_bet": 500
}
```

## Architecture

### Core Components

#### 1. Backend (Python)

**Game Engine (`engine/`)**
- `card.py` - Card and Deck classes
- `hand.py` - Hand evaluation logic
- `game.py` - Blackjack game rules and flow
- `dealer.py` - Dealer behavior (hit on 16, stand on 17)

**Strategy System (`strategies/`)**
- `base_strategy.py` - Abstract base classes
  - `BettingStrategy` - Determines bet size
  - `PlayingStrategy` - Determines playing actions (hit/stand/split/double/surrender)
  - `Strategy` - Aggregates betting + playing strategies
- `betting/`
  - `flat_bet.py` - Fixed bet amount
  - `martingale.py` - Progressive betting (double after loss)
  - `kelly_criterion.py` - Kelly criterion betting
- `playing/`
  - `basic_strategy.py` - Optimal playing decisions
  - `basic_strategy_deviations.py` - Count-based strategy deviations
- `presets/`
  - `basic_flat.py` - Basic strategy + flat betting
  - `basic_martingale.py` - Basic strategy + Martingale
  - `card_counting.py` - Hi-Lo counting with betting + playing deviations

**Simulator (`simulator/`)**
- `session.py` - Single simulation session
- `runner.py` - Batch simulation runner
- `statistics.py` - Statistical analysis (ROI, variance, risk of ruin)

**API (`api/`)**
- `server.py` - FastAPI/Flask REST API
- Endpoints:
  - `POST /simulate` - Run simulation
  - `GET /strategies` - List available strategies
  - `GET /results/{session_id}` - Get results
  - `POST /compare` - Compare multiple strategies

**Data Layer (`data/`)**
- `models.py` - Data models (Session, Result, Statistics)
- `storage.py` - SQLite/JSON storage for results
- `export.py` - Export to CSV/JSON

#### 2. Frontend

**Technology Stack**
- React/Vue.js or simple HTML/CSS/JavaScript
- Chart.js or Plotly for visualizations

**Pages/Components**

**Strategy Configuration Panel**
- Select strategy type
- Configure parameters (initial bet, bankroll, etc.)
- Set simulation parameters (hands, sessions)

**Simulation Control**
- Start/Stop/Pause simulation
- Real-time progress indicator
- Quick vs. detailed mode

**Results Dashboard**
- Bankroll over time (line chart)
- Win/Loss distribution (bar chart)
- Key metrics cards:
  - Total hands played
  - Win rate
  - Average bet size
  - Final bankroll
  - ROI percentage
  - Max drawdown
  - Risk of ruin estimate

**Strategy Comparison View**
- Side-by-side comparison table
- Overlay charts for multiple strategies
- Statistical significance tests

**Hand History Viewer**
- Detailed hand-by-hand playback
- Filter by outcome
- Export functionality

## Data Flow

```
User Input (Frontend)
    ↓
API Request
    ↓
Simulation Runner
    ↓
Game Engine (multiple iterations)
    ↓
Strategy Plugin (betting decisions)
    ↓
Statistics Aggregation
    ↓
Results Storage
    ↓
API Response
    ↓
Frontend Visualization
```

## Key Classes

### Backend

```python
# Betting Strategy - determines bet size
class BettingStrategy(ABC):
    def __init__(self, config: dict):
        self.config = config
    
    @abstractmethod
    def get_bet(self, bankroll: float, history: list) -> float:
        pass
    
    @abstractmethod
    def reset(self):
        pass

# Playing Strategy - determines actions
class PlayingStrategy(ABC):
    def __init__(self, config: dict):
        self.config = config
    
    @abstractmethod
    def get_action(self, player_hand, dealer_upcard, game_state) -> Action:
        # Returns: HIT, STAND, DOUBLE, SPLIT, SURRENDER
        pass
    
    @abstractmethod
    def reset(self):
        pass

# Aggregate Strategy - combines betting + playing
class Strategy:
    def __init__(self, betting: BettingStrategy, playing: PlayingStrategy):
        self.betting = betting
        self.playing = playing
    
    def get_bet(self, bankroll: float, history: list) -> float:
        return self.betting.get_bet(bankroll, history)
    
    def get_action(self, player_hand, dealer_upcard, game_state) -> Action:
        return self.playing.get_action(player_hand, dealer_upcard, game_state)
    
    def reset(self):
        self.betting.reset()
        self.playing.reset()

# Game Engine
class BlackjackGame:
    def __init__(self, num_decks: int = 6):
        self.shoe = Shoe(num_decks)
        self.dealer = Dealer()
    
    def play_hand(self, bet: float, strategy: Strategy) -> Result:
        pass

# Simulator
class SimulationRunner:
    def run(self, strategy: Strategy, 
            num_hands: int, 
            initial_bankroll: float,
            callback: callable = None) -> SimulationResult:
        pass

# Results
class SimulationResult:
    bankroll_history: list
    hands_played: int
    wins: int
    losses: int
    pushes: int
    final_bankroll: float
    
    def calculate_statistics(self) -> Statistics:
        pass
```

### Frontend

```javascript
// Strategy Configuration
class StrategyConfig {
    strategyType: string
    parameters: object
    simulationSettings: {
        numHands: number
        initialBankroll: number
        numSessions: number
    }
}

// Results Display
class SimulationResults {
    sessionId: string
    statistics: Statistics
    bankrollHistory: number[]
    
    render(): void
    exportData(): void
}
```

## API Endpoints

```
POST /api/v1/simulate
Body: {
    "strategy": "martingale",
    "config": {
        "initial_bet": 10,
        "max_bet": 500,
        "progression": 2
    },
    "simulation": {
        "num_hands": 1000,
        "initial_bankroll": 1000,
        "num_sessions": 100
    }
}
Response: {
    "session_id": "uuid",
    "status": "running"
}

GET /api/v1/results/{session_id}
Response: {
    "statistics": {...},
    "bankroll_history": [...],
    "hand_history": [...]
}

POST /api/v1/compare
Body: {
    "strategies": ["martingale", "flat_bet"],
    "configs": [{...}, {...}],
    "simulation": {...}
}
Response: {
    "comparison_id": "uuid",
    "results": [...]
}
```

## File Structure

```
blackjack_tester/
├── backend/
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── card.py
│   │   ├── deck.py
│   │   ├── hand.py
│   │   ├── game.py
│   │   └── dealer.py
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── base_strategy.py
│   │   ├── martingale.py
│   │   ├── flat_bet.py
│   │   ├── card_counting.py
│   │   └── kelly_criterion.py
│   ├── simulator/
│   │   ├── __init__.py
│   │   ├── session.py
│   │   ├── runner.py
│   │   └── statistics.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── server.py
│   │   └── routes.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── storage.py
│   ├── tests/
│   │   └── ...
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── StrategyConfig.js
│   │   │   ├── SimulationControl.js
│   │   │   ├── ResultsDashboard.js
│   │   │   ├── ComparisonView.js
│   │   │   └── Charts.js
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
├── AGENTS.md
└── README.md
```

## Implementation Phases

### Phase 1: Core Engine
1. Implement card, deck, and hand classes
2. Build basic blackjack game logic
3. Create dealer behavior
4. Unit tests for game rules

### Phase 2: Strategy System
1. Define base strategy interface
2. Implement 3-4 common strategies
3. Create strategy registry/factory
4. Test strategy plugins

### Phase 3: Simulator
1. Build single-session simulator
2. Add batch simulation capability
3. Implement statistics calculation
4. Add progress callbacks

### Phase 4: Backend API
1. Set up FastAPI/Flask server
2. Implement core endpoints
3. Add data persistence
4. API documentation

### Phase 5: Frontend
1. Create basic UI layout
2. Strategy configuration form
3. Real-time simulation display
4. Results visualization

### Phase 6: Advanced Features
1. Strategy comparison tools
2. Export functionality
3. Advanced statistics
4. Performance optimization

## Key Features

### Strategy Plugin System
- Easy to add new strategies
- Configuration validation
- Strategy metadata (name, description, parameters)
- Hot-reload capability

### Statistical Analysis
- Expected value calculation
- Standard deviation
- Confidence intervals
- Risk of ruin probability
- Sharpe ratio
- Maximum drawdown

### Visualization
- Real-time bankroll chart
- Win/loss distribution
- Bet size distribution
- Strategy comparison overlays
- Heat maps for optimal parameters

### Performance Considerations
- Vectorized operations for batch simulations
- Async API for long-running simulations
- Caching for repeated simulations
- Database indexing for quick retrieval

## Configuration Example

```yaml
# config.yaml
game_rules:
  num_decks: 6
  dealer_hits_soft_17: false
  blackjack_payout: 1.5
  surrender_allowed: true
  double_after_split: true
  resplit_aces: false

simulation:
  default_hands: 1000
  default_sessions: 100
  default_bankroll: 1000

strategies:
  martingale:
    initial_bet: 10
    progression: 2
    max_bet: 500
  
  flat_bet:
    bet_amount: 10
  
  card_counting:
    initial_bet: 10
    true_count_multiplier: 5
    min_bet: 10
    max_bet: 500
```

## Testing Strategy

1. Unit tests for game logic (card values, hand evaluation)
2. Integration tests for full game flow
3. Strategy validation tests
4. Statistical tests (verify expected outcomes over large samples)
5. API endpoint tests
6. Frontend component tests
7. End-to-end tests

## Future Enhancements

- Multi-player simulation
- Tournament mode
- Machine learning strategy optimization
- Real-time multiplayer testing
- Mobile app
- Cloud deployment with scalable workers
- Strategy marketplace/sharing
- Advanced card counting systems
- Side bet analysis
- Live casino rule variations
