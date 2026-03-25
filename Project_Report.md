# AI-Driven Agents and the Winner’s Curse: A Game Theoretic Model of Construction Tender Bidding

**Group Members:**
- [Student Name], [Student ID]
- [Student Name], [Student ID]
- [Student Name], [Student ID]
- [Student Name], [Student ID]
- [Student Name], [Student ID]

## Executive Summary
This project investigates the dynamics of construction tender bidding—a competitive first-price sealed-bid procurement auction—where the underlying cost of the project is uncertain and inherently correlated amongst all bidders (Common Value). Because the bidder with the most optimistic (and thus, most frequently incorrect) estimate wins, there is an innate statistical risk known as the **Winner's Curse**. 

To explore this real-world problem, we implement a novel multi-agent reinforcement learning (MARL) simulation where five independent AI agents act as contractors. These agents utilize model-free Q-Learning to learn optimal bid-markup strategies over time through repeated participation in simulated auctions. Results demonstrate that naive bidding rapidly results in systemic bankruptcies due to the Winner's Curse. However, by observing competitive outcomes, the AI agents learn to strategically over-bid (bid-shade) by adopting high markup margins up to 15-20%, reaching an emergent empirical Nash Equilibrium. This study showcases a profound application of theoretical Game Theory in the construction industry and provides computational evidence of bounded rationality converging to optimal strategies.

---
## 1. Introduction and Problem Motivation
The construction industry heavily relies on the tender bidding process to award projects. The conventional structure is a **First-Price Sealed-Bid Procurement Auction**, where the employer awards the contract to the lowest bidder. 
However, contractors generate estimates based on complex, incomplete structural plans and macroeconomic variables, creating a **Common Value Auction** environment. The true cost $C$ is unknown but shared by whoever wins.

Because winning strictly implies that a contractor had the lowest estimate, the "winner" often happens to be the single agent who underestimated the true project cost the most. This phenomenon, formalized as the **Winner’s Curse**, plagues real-world construction networks, often leading to cost overruns, delayed projects, and contractor bankruptcies. 

Traditional game theory assumes perfect hyper-rationality where bidders mathematically compute the precise Bayes-Nash Equilibrium factoring in order statistics. In reality, contractors adapt through experience. This project explores a **novel technical approach**: replacing static game theory equations with a Multi-Agent Reinforcement Learning (MARL) environment, where computational agents act as boundedly rational contractors learning from positive and negative profit feedback over time.

---
## 2. Related Work and Study
The foundational game-theoretic treatment of common value auctions and the Winner's Curse was established by **Milgrom and Weber (1982)**, who demonstrated how affiliated private signals can skew expected valuations. 
**Hong and Shum (2002)** further elaborated empirically on construction procurement, proving that as competition (the number of bidders) increases, bidding behavior changes. Surprisingly, more competition can cause rational bidders to bid *higher* or "shade" their bids further to offset the magnified statistical risk of the Winner's curse. 
Building upon these theories, **Easley and Kleinberg (2010)** analyze how learning mechanisms can converge towards Nash Equilibria. The integration of Q-learning into sealed-bid auctions is an emerging field, providing realistic frameworks for algorithmic pricing and contractor bidding simulations.

---
## 3. Model and Problem Formulation

### 3.1. The Procurement Auction Game
We formulate a game of $N=5$ symmetric, risk-neutral contractors. 
For every distinct construction project (an episode), the environment generates a **True Cost** $C$:
$C \sim \text{Uniform}(80, 120)$

Agents do not observe $C$. Instead, they generate private, noisy estimates (Signals) $s_i$:
$s_i \sim \text{Uniform}(C - 15, C + 15)$

The strategic variable for agent $i$ is its **Markup Action** ($m_i \in [0.0, 0.40]$). Thus, the submitted bid $b_i$ is:
$b_i = s_i \times (1 + m_i)$

### 3.2. Payoff Construction
The contractor with the lowest bid wins the auction constraint. The payoff $\pi_i$ is:
$\pi_i = \begin{cases} b_i - C & \text{if } i = \text{argmin}_j(b_j) \\ 0 & \text{otherwise} \end{cases}$

Note that the profit is relative to the **True Cost** $C$, not the agent's estimate $s_i$. If an agent with a highly underestimated signal $s_i = 70$ (where $C = 85$) wins with a 10% markup ($b_i = 77$), they incur a loss of $-8$.

### 3.3. Learning Formulation (Q-Learning)
Each agent operates an independent Q-table containing expected rewards for discretized markups inside the action space $\mathcal{A} = \{0\%, 2\%, 4\%, \dots, 40\%\}$. 
Agents utilize an $\epsilon$-greedy policy to explore the action space. Upon executing action $a$ and receiving reward $\pi_i$, the Q-Value updates via:
$Q(a) \leftarrow Q(a) + \alpha [\pi_i - Q(a)]$
where $\alpha = 0.05$ is the temporal learning rate. Over 100,000 simulated iterations, agents adapt their markup behaviors purely from realized profit signals.

---
## 4. Analysis and Result Discussion

The simulation inherently tests whether independent agents can empirically avoid the Winner's Curse without explicit mathematical knowledge of the game structure.

### 4.1. The Initial Trap (Winner's Curse)
In early iterations, agents explore uniformly across the markup threshold. As shown in **Figure: Average Rolling Profit Over Time**, rolling profits plummet below $\$0$ initially. Because low markups are competitive, naive agents win frequently but constantly incur significant capital losses—empirically demonstrating the Winner's Curse. 

![Average Rolling Profit Over Time](./profit_over_time.png)

### 4.2. Emergence of Bid Shading
As learning episodes progress, negative rewards heavily penalize low-markup actions. The agents independently learn the concept of **Bid Shading**—artificially inflating their bids by higher markup margins to account for the unobserved statistical hazard.
**Figure: Learned Markup over Time** shows the rapid and steady escalation of average markups across the population. It eventually converges dynamically around an approximate mean of ~15-20% markup.

![Learned Markup of Agents Over Time](./markup_over_time.png)

### 4.3. Nash Equilibrium Convergence
Looking at the final learned Q-Values (**Figure: Q-Values for Different Markups**), all agents unanimously develop peak expected profits at the ~18-22% markup bracket. Bidding too low yields the Winner's Curse (negative payoff), and bidding too high yields $0$ profitability because the agent never wins the tender. The peak of the Q-Value parabola demonstrates an empirically reached **Nash Equilibrium**. At the convergence state, the contractors achieve sustained positive profitability, safely navigating the extreme information asymmetry of the industry.

![Q-Values for Different Markups](./q_values.png)

---
## 5. Societal / Industry Impact
This framework highlights a critical insight for the construction and civil engineering sector: underbidding driven by hyper-competition leads to systemic failures. Furthermore, this opens the door for algorithmic contracting tools, where predictive AI uses historic competitor behavior to recommend dynamically safe bid ranges, ultimately optimizing industry supply chains.

---
## 6. References
1. Milgrom, P. R., & Weber, R. J. (1982). *A Theory of Auctions and Competitive Bidding*. Econometrica, 50(5), 1089-1122.
2. Hong, H., & Shum, M. (2002). *Increasing Competition and the Winner's Curse: Evidence from Procurement*. The Review of Economic Studies.
3. Watkins, C. J. C. H., & Dayan, P. (1992). *Q-learning*. Machine Learning, 8(3), 279-292.
4. Kagel, J. H., & Levin, D. (1986). *The Winner's Curse and Public Information in Common Value Auctions*. The American Economic Review, 76(5), 894-920.
