from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import numpy as np
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimulationParams(BaseModel):
    num_contractors: int = 5
    episodes: int = 50000
    auction_type: str = "first_price"
    min_cost: float = 80.0
    max_cost: float = 120.0

@app.post("/api/simulate")
def run_simulation(params: SimulationParams):
    np.random.seed(42)
    
    N_AGENTS = params.num_contractors
    N_EPISODES = params.episodes
    MARKUP_ACTIONS = np.linspace(0.0, 0.40, 21)
    N_ACTIONS = len(MARKUP_ACTIONS)
    LEARNING_RATE = 0.05
    
    EPSILON_START = 1.0
    EPSILON_END = 0.02
    EPSILON_DECAY = (EPSILON_END / EPSILON_START) ** (1 / max(1, N_EPISODES * 0.8))
    
    Q = np.zeros((N_AGENTS, N_ACTIONS))
    
    average_markups = []
    average_profits = []
    rolling_profits = np.zeros(N_AGENTS)
    
    plot_interval = N_EPISODES // 100 if N_EPISODES >= 100 else 1
    
    for episode in range(N_EPISODES):
        epsilon = max(EPSILON_END, EPSILON_START * (EPSILON_DECAY ** episode))
        
        true_cost = np.random.uniform(params.min_cost, params.max_cost)
        
        variance = true_cost * 0.15
        signals = np.random.uniform(true_cost - variance, true_cost + variance, N_AGENTS)
        
        actions = np.zeros(N_AGENTS, dtype=int)
        bids = np.zeros(N_AGENTS)
        
        for i in range(N_AGENTS):
            if np.random.rand() < epsilon:
                actions[i] = np.random.randint(N_ACTIONS)
            else:
                actions[i] = np.argmax(Q[i])
                
            markup = MARKUP_ACTIONS[actions[i]]
            bids[i] = signals[i] * (1 + markup)
            
        winner = -1
        revenue = 0.0
        
        if params.auction_type == "first_price":
            winner = np.argmin(bids)
            revenue = bids[winner]
        elif params.auction_type == "second_price":
            winner = np.argmin(bids)
            sorted_bids = np.sort(bids)
            revenue = sorted_bids[1] if N_AGENTS > 1 else bids[winner]
        elif params.auction_type == "average_bid":
            avg_bid = np.mean(bids)
            valid_bids = [(i, b) for i, b in enumerate(bids) if b <= avg_bid]
            if not valid_bids: 
                valid_bids = [(i, b) for i, b in enumerate(bids)]
            winner_idx, winner_bid = max(valid_bids, key=lambda x: x[1])
            winner = winner_idx
            revenue = winner_bid
            
        rewards = np.zeros(N_AGENTS)
        profit = revenue - true_cost
        rewards[winner] = profit
        
        for i in range(N_AGENTS):
            Q[i, actions[i]] = Q[i, actions[i]] + LEARNING_RATE * (rewards[i] - Q[i, actions[i]])
            
        rolling_profits[winner] = 0.999 * rolling_profits[winner] + 0.001 * profit
        for i in range(N_AGENTS):
            if i != winner:
                rolling_profits[i] = 0.999 * rolling_profits[i]
                
        if episode % plot_interval == 0:
            greedy_actions = np.argmax(Q, axis=1)
            avg_markup = np.mean(MARKUP_ACTIONS[greedy_actions])
            average_markups.append(float(avg_markup))
            average_profits.append(float(np.mean(rolling_profits)))
    
    episodes_x = [i * plot_interval for i in range(len(average_markups))]
    
    q_values_data = {}
    for i in range(N_AGENTS):
        q_values_data[f"Agent_{i+1}"] = Q[i].tolist()
        
    return {
        "episodes": episodes_x,
        "markups": average_markups,
        "profits": average_profits,
        "markup_actions": MARKUP_ACTIONS.tolist(),
        "q_values": q_values_data
    }

# Serve static files
static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")