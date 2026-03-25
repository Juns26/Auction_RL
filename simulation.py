import numpy as np
import matplotlib.pyplot as plt
import os

# Ensure working directory is set to file location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Set seed for reproducibility
np.random.seed(42)

# Parameters
N_AGENTS = 5
N_EPISODES = 100000
MARKUP_ACTIONS = np.linspace(0.0, 0.40, 21) # Markups from 0% to 40%, 2% increments
N_ACTIONS = len(MARKUP_ACTIONS)
LEARNING_RATE = 0.05

EPSILON_START = 1.0
EPSILON_END = 0.05
EPSILON_DECAY = 0.99995

Q = np.zeros((N_AGENTS, N_ACTIONS))

average_markups = []
average_profits = []
rolling_profits = np.zeros(N_AGENTS)

for episode in range(N_EPISODES):
    epsilon = max(EPSILON_END, EPSILON_START * (EPSILON_DECAY ** episode))
    
    true_cost = np.random.uniform(80, 120)
    signals = np.random.uniform(true_cost - 15, true_cost + 15, N_AGENTS)
    
    actions = np.zeros(N_AGENTS, dtype=int)
    bids = np.zeros(N_AGENTS)
    
    for i in range(N_AGENTS):
        if np.random.rand() < epsilon:
            actions[i] = np.random.randint(N_ACTIONS)
        else:
            actions[i] = np.argmax(Q[i])
            
        markup = MARKUP_ACTIONS[actions[i]]
        bids[i] = signals[i] * (1 + markup)
        
    winner = np.argmin(bids)
    
    rewards = np.zeros(N_AGENTS)
    # The winner's profit is their bid minus the TRUE cost
    profit = bids[winner] - true_cost
    rewards[winner] = profit
    
    for i in range(N_AGENTS):
        Q[i, actions[i]] = Q[i, actions[i]] + LEARNING_RATE * (rewards[i] - Q[i, actions[i]])
        
    rolling_profits[winner] = 0.999 * rolling_profits[winner] + 0.001 * profit
    for i in range(N_AGENTS):
        if i != winner:
            rolling_profits[i] = 0.999 * rolling_profits[i]
            
    if episode % 500 == 0:
        greedy_actions = np.argmax(Q, axis=1)
        avg_markup = np.mean(MARKUP_ACTIONS[greedy_actions])
        average_markups.append(avg_markup)
        average_profits.append(np.mean(rolling_profits))

plt.figure(figsize=(10, 6))
plt.plot(np.arange(len(average_markups))*500, average_markups, color='#2ca02c', linewidth=2.5)
plt.title('Learned Markup of Q-Learning Bidders Over Time', fontsize=14)
plt.xlabel('Episodes', fontsize=12)
plt.ylabel('Average Markup Policy', fontsize=12)
plt.grid(True, alpha=0.3)
plt.savefig('markup_over_time.png', dpi=300, bbox_inches='tight')
plt.close()

plt.figure(figsize=(10, 6))
plt.plot(np.arange(len(average_profits))*500, average_profits, color='#d62728', linewidth=2.5)
plt.title('Average Rolling Profit Over Time', fontsize=14)
plt.xlabel('Episodes', fontsize=12)
plt.ylabel('Profit', fontsize=12)
plt.axhline(0, color='black', linestyle='--', linewidth=1.5)
ymin, ymax = plt.ylim()
plt.text(N_EPISODES*0.5, ymax*0.5, 'Positive Profit (Winner\'s Curse Avoided)', color='black', ha='center')
if ymin < 0:
    plt.text(N_EPISODES*0.5, ymin*0.5, 'Negative Profit (Winner\'s Curse)', color='black', ha='center')
plt.grid(True, alpha=0.3)
plt.savefig('profit_over_time.png', dpi=300, bbox_inches='tight')
plt.close()

plt.figure(figsize=(10, 6))
for i in range(N_AGENTS):
    plt.plot(MARKUP_ACTIONS, Q[i], label=f'Contractor {i+1}', alpha=0.8, linewidth=2)
plt.title('Learned Expected Profit (Q-Values) for Different Markups', fontsize=14)
plt.xlabel('Markup Action', fontsize=12)
plt.ylabel('Expected Profit (Q-value)', fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('q_values.png', dpi=300, bbox_inches='tight')
plt.close()

print("Simulation finished, plots generated!")
