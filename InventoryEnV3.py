# dunnhumby_inventory_dqn_notebook.py
# Jupyter-style runnable script for local use (also works as a .py script).
# Purpose: EDA on Dunnhumby Complete Journey sample, build weekly pivot demand for top-K SKUs,
# create environment from data, train a small shared DQN on top-200 SKUs and plot learning curve.

# Requirements:
# pip install pandas numpy matplotlib torch tqdm seaborn

import os
import math
import random
import pickle
from collections import deque, namedtuple
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import trange

# -----------------------------
# 1) Data load & EDA utilities
# -----------------------------
DATA_DIR = Path("C:/Users/HP ZBook 15/.cache/kagglehub/datasets/frtgnn/dunnhumby-the-complete-journey/versions/1/")  # change to your local path

def find_transaction_file(data_dir):
    candidates = [
        "transaction_data.csv", "transactions.csv", "transaction.csv",
        "transaction_data.csv.gz"
    ]
    for fn in candidates:
        p = data_dir / fn
        if p.exists():
            return p
    # fallback: first csv with 'trans' in name
    for p in data_dir.glob("*.csv"):
        if 'trans' in p.name.lower():
            return p
    raise FileNotFoundError("Transaction CSV not found in " + str(data_dir))

print("Looking for transaction file in:", DATA_DIR)

# Basic EDA function
def quick_eda(trans_df, product_col='product_id'):
    print("Rows:", len(trans_df))
    print("Columns:", trans_df.columns.tolist())
    if product_col in trans_df.columns:
        print("Unique SKUs:", trans_df[product_col].nunique())
    print(trans_df.head())

# -----------------------------
# 2) Prepare weekly pivot demand
# -----------------------------

def detect_time_col(df):
    for col in df.columns:
        lc = col.lower()
        if 'week' in lc and ('no' in lc or 'number' in lc or lc=='week' or 'week_no' in lc):
            return col, 'week'
        if lc in ('date','trans_date','transaction_date','t_date'):
            return col, 'date'
        if 'day' in lc:
            return col, 'date'
    # fallback try parse
    for col in df.columns:
        try:
            pd.to_datetime(df[col].iloc[:20])
            return col, 'date'
        except Exception:
            continue
    return None, None


def build_weekly_pivot(trans_df, product_col='product_id'):
    # detect qty col
    qty_candidates = ['quantity','qty','units','sales_qty','quantity_purchased','quantity_sold']
    qty_col = None
    for c in qty_candidates:
        if c in trans_df.columns:
            qty_col = c
            break
    if qty_col is None:
        for c in trans_df.columns:
            if 'qty' in c.lower() or 'quantity' in c.lower() or 'units' in c.lower():
                qty_col = c
                break
    if qty_col is None:
        raise ValueError('Quantity column not found')

    time_col, ttype = detect_time_col(trans_df)
    if time_col is None:
        raise ValueError('Time column not detected')

    df = trans_df.copy()
    if ttype == 'date':
        df[time_col] = pd.to_datetime(df[time_col])
        df['week'] = df[time_col].dt.to_period('W').apply(lambda r: r.start_time)
    else:
        df['week'] = df[time_col]

    # aggregate
    agg = df.groupby(['week', product_col])[qty_col].sum().reset_index()
    pivot = agg.pivot(index='week', columns=product_col, values=qty_col).fillna(0).sort_index()
    return pivot

# -----------------------------
# 3) Select top-K SKUs
# -----------------------------

def select_topk(pivot_df, k=200):
    totals = pivot_df.sum(axis=0).sort_values(ascending=False)
    topk = totals.iloc[:k].index.tolist()
    return pivot_df[topk].astype(int)

# -----------------------------
# 4) Environment from data
# -----------------------------
class MultiSKUInventoryEnvFromData:
    def __init__(self, demand_matrix, weeks, lead_time=2, horizon_weeks=12, promo_matrix=None):
        self.demand_matrix = np.asarray(demand_matrix, dtype=float)  # shape (n_weeks, n_skus)
        self.weeks = weeks
        self.n_weeks, self.n_skus = self.demand_matrix.shape
        self.lead_time = lead_time
        self.horizon = horizon_weeks
        self.promo_matrix = promo_matrix if promo_matrix is not None else np.zeros_like(self.demand_matrix, dtype=int)
        self.mu = np.maximum(0.001, np.mean(self.demand_matrix, axis=0))
        self.sigma = np.sqrt(np.maximum(1e-6, self.mu))
        self.reset(start_week_idx=0)

    def reset(self, start_week_idx=0):
        self.start_week = start_week_idx % self.n_weeks
        self.week_cursor = self.start_week
        self.I = np.maximum(0, np.round(1.5 * self.mu * self.lead_time).astype(int))
        self.oo = np.zeros((self.n_skus, self.lead_time), dtype=int)
        self.backlog = np.zeros(self.n_skus, dtype=int)
        self.t = 0
        self.promo = self.promo_matrix[self.week_cursor] if self.promo_matrix is not None else np.zeros(self.n_skus, dtype=int)
        return self._get_full_state()

    def step(self, orders, stochastic=False, promo_boost=0.2):
        assert len(orders) == self.n_skus
        holding_cost_per_unit = 0.01
        stockout_cost_per_unit = 1.0
        order_fixed_cost = 0.5
        order_unit_cost = 0.0

        self.oo[:, -1] += orders
        hist = self.demand_matrix[self.week_cursor]
        if stochastic:
            lam = np.clip(hist, 0, 1e8)
            demand = np.random.poisson(lam).astype(int)
        else:
            demand = np.round(hist).astype(int)

        promo_flags = self.promo_matrix[self.week_cursor] if self.promo_matrix is not None else np.zeros_like(demand)
        demand = (demand * (1 + promo_boost * promo_flags)).astype(int)

        # serve
        available = self.I.copy()
        served = np.minimum(available, demand + self.backlog)
        serve_backlog = np.minimum(self.backlog, served)
        self.backlog -= serve_backlog
        served_new = served - serve_backlog
        unfilled = (demand - served_new)
        self.backlog += np.maximum(0, unfilled)
        self.I -= (served_new + serve_backlog)

        holding_cost = holding_cost_per_unit * np.sum(self.I)
        stockout_cost = stockout_cost_per_unit * np.sum(self.backlog)
        order_cost = order_fixed_cost * np.sum(orders > 0) + order_unit_cost * np.sum(orders)
        reward = -(holding_cost + stockout_cost + order_cost)

        arrivals = self.oo[:, 0].copy()
        if self.lead_time > 1:
            self.oo[:, :-1] = self.oo[:, 1:]
        self.oo[:, -1] = 0
        self.I += arrivals

        self.week_cursor = (self.week_cursor + 1) % self.n_weeks
        self.promo = self.promo_matrix[self.week_cursor] if self.promo_matrix is not None else np.zeros(self.n_skus, dtype=int)
        self.t += 1
        done = (self.t >= self.horizon)
        return self._get_full_state(), reward, done, {'demand': demand, 'arrivals': arrivals}

    def _get_full_state(self):
        return {
            'I': self.I.copy(),
            'oo': self.oo.copy(),
            'backlog': self.backlog.copy(),
            'promo': self.promo.copy(),
            'mu': self.mu.copy(),
            'sigma': self.sigma.copy(),
            't': self.t,
            'week': self.week_cursor
        }

# -----------------------------
# 5) Feature extractor (same as earlier)
# -----------------------------

def sku_feature_vector(state, idx, lead_time=2):
    I = float(state['I'][idx])
    oo = state['oo'][idx]
    backlog = float(state['backlog'][idx])
    promo = float(state['promo'][idx])
    mu = float(state['mu'][idx])
    sigma = float(state['sigma'][idx])
    t = state['t']

    IP = I + oo.sum() - backlog
    oo_due1 = float(oo[0]) if lead_time >= 1 else 0.0
    oo_other = float(max(0, oo.sum() - oo_due1))
    sigma_L = math.sqrt(max(1e-6, mu * max(1, lead_time)))

    feats = np.array([
        I / sigma_L,
        IP / sigma_L,
        oo_due1 / sigma_L,
        oo_other / sigma_L,
        backlog / sigma_L,
        mu / sigma_L,
        sigma / sigma_L,
        math.sin(2*math.pi*((t % 7)/7)),
        math.cos(2*math.pi*((t % 7)/7)),
        promo
    ], dtype=np.float32)
    return feats

# -----------------------------
# 6) Small DQN agent (shared network)
# -----------------------------

class QNetwork(nn.Module):
    def __init__(self, input_dim, n_actions, hidden=[64,64]):
        super().__init__()
        layers = []
        last = input_dim
        for h in hidden:
            layers.append(nn.Linear(last, h))
            layers.append(nn.ReLU())
            last = h
        layers.append(nn.Linear(last, n_actions))
        self.net = nn.Sequential(*layers)
    def forward(self, x):
        return self.net(x)

Transition = namedtuple('Transition', ('state','action','reward','next_state','done'))

class ReplayBuffer:
    def __init__(self, capacity=100000):
        self.buffer = deque(maxlen=capacity)
    def push(self, *args):
        self.buffer.append(Transition(*args))
    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        return Transition(*zip(*batch))
    def __len__(self):
        return len(self.buffer)

class DQNAgent:
    def __init__(self, input_dim, n_actions, lr=1e-3, gamma=0.99, device='cpu'):
        self.policy = QNetwork(input_dim, n_actions).to(device)
        self.target = QNetwork(input_dim, n_actions).to(device)
        self.target.load_state_dict(self.policy.state_dict())
        self.opt = optim.Adam(self.policy.parameters(), lr=lr)
        self.gamma = gamma
        self.device = device
        self.n_actions = n_actions
        self.steps = 0

    def q_values(self, states):
        st = torch.tensor(states, dtype=torch.float32, device=self.device)
        return self.policy(st)

    def act_batch(self, state_batch, eps=0.1):
        # state_batch: np.array (B, input_dim)
        B = state_batch.shape[0]
        if np.random.rand() < eps:
            return np.random.randint(self.n_actions, size=B)
        st = torch.tensor(state_batch, dtype=torch.float32, device=self.device)
        with torch.no_grad():
            q = self.policy(st).cpu().numpy()
        return np.argmax(q, axis=1)

    def update(self, buffer, batch_size=64, tau=0.01):
        if len(buffer) < batch_size:
            return
        b = buffer.sample(batch_size)
        state = torch.tensor(np.stack(b.state), dtype=torch.float32, device=self.device)
        action = torch.tensor(b.action, dtype=torch.int64, device=self.device).unsqueeze(1)
        reward = torch.tensor(b.reward, dtype=torch.float32, device=self.device).unsqueeze(1)
        next_state = torch.tensor(np.stack(b.next_state), dtype=torch.float32, device=self.device)
        done = torch.tensor(b.done, dtype=torch.float32, device=self.device).unsqueeze(1)

        q_vals = self.policy(state).gather(1, action)
        with torch.no_grad():
            q_next = self.target(next_state).max(1)[0].unsqueeze(1)
            q_target = reward + (1 - done) * self.gamma * q_next
        loss = nn.functional.mse_loss(q_vals, q_target)
        self.opt.zero_grad()
        loss.backward()
        self.opt.step()

        for p, tp in zip(self.policy.parameters(), self.target.parameters()):
            tp.data.copy_(tau * p.data + (1 - tau) * tp.data)

# -----------------------------
# 7) Training + plotting utilities
# -----------------------------

def train_dqn_on_data(env, episodes=30, action_buckets=None, device='cpu'):
    if action_buckets is None:
        action_buckets = np.array([0,1,2,5,10,20,50], dtype=int)
    n_actions = len(action_buckets)
    input_dim = 10
    agent = DQNAgent(input_dim, n_actions, lr=1e-3, gamma=0.9, device=device)
    buffer = ReplayBuffer(capacity=200000)

    eps_start, eps_end = 0.5, 0.02
    eps_decay = episodes * env.n_skus * env.horizon / 10.0

    total_rewards = []
    avg_rewards = []

    for ep in trange(episodes, desc='Episodes'):
        # random start week for more diversity
        start = random.randint(0, env.n_weeks - 1)
        state = env.reset(start_week_idx=start)
        done = False
        ep_reward = 0.0

        while not done:
            M = min(256, env.n_skus)
            skus = np.random.choice(env.n_skus, size=M, replace=False)
            feats = np.stack([sku_feature_vector(state, s, lead_time=env.lead_time) for s in skus])

            ttotal = agent.steps
            eps = max(eps_end, eps_start - (eps_start - eps_end) * (ttotal / max(1, eps_decay)))
            act_idxs = agent.act_batch(feats, eps=eps)

            orders = np.zeros(env.n_skus, dtype=int)
            for i, s in enumerate(skus):
                base = action_buckets[act_idxs[i]]
                scale = int(max(1, round(state['mu'][s] / 5.0)))
                orders[s] = int(base * scale)

            next_state, reward, done, info = env.step(orders)
            ep_reward += reward

            for i, s in enumerate(skus):
                st_vec = feats[i]
                act = int(act_idxs[i])
                r = float(reward) / env.n_skus  # distribute reward as small signal
                next_vec = sku_feature_vector(next_state, s, lead_time=env.lead_time)
                buffer.push(st_vec, act, r, next_vec, float(done))

            agent.update(buffer, batch_size=128, tau=0.005)
            agent.steps += 1
            state = next_state

        total_rewards.append(ep_reward)
        avg_rewards.append(np.mean(total_rewards[-5:]))
        if (ep+1) % 5 == 0:
            print(f"Ep {ep+1}/{episodes} - ep_reward: {ep_reward:.2f}, avg5: {avg_rewards[-1]:.2f}, eps: {eps:.3f}")

    return agent, total_rewards, avg_rewards


def plot_rewards(total_rewards, avg_rewards=None):
    plt.figure(figsize=(10,5))
    plt.plot(total_rewards, label='Episode reward')
    if avg_rewards is not None:
        plt.plot(avg_rewards, label='Moving average (5)')
    plt.xlabel('Episode')
    plt.ylabel('Total reward')
    plt.title('Learning curve - DQN Inventory Agent (data-driven)')
    plt.legend()
    plt.grid(True)
    plt.show()

# -----------------------------
# 8) Example end-to-end runner (if running as script)
# -----------------------------
if __name__ == '__main__':
    # 1. Load transactions (adjust path)
    tx_file = find_transaction_file(DATA_DIR)
    print('Using', tx_file)
    tx = pd.read_csv(tx_file, low_memory=False)

    # Quick EDA
    quick_eda(tx)

    # 2. Build weekly pivot
    print('Building weekly pivot...')
    pivot = build_weekly_pivot(tx, product_col='product_id')
    print('Pivot shape (weeks x skus):', pivot.shape)

    # 3. Select top-200 SKUs
    topk_df = select_topk(pivot, k=200)
    print('Selected topk shape:', topk_df.shape)

    # 4. Build env
    demand_matrix = topk_df.values  # (n_weeks, 200)
    weeks = list(topk_df.index)
    env = MultiSKUInventoryEnvFromData(demand_matrix, weeks, lead_time=2, horizon_weeks=12)

    # 5. Train small DQN
    agent, total_rewards, avg_rewards = train_dqn_on_data(env, episodes=30, action_buckets=[0,1,2,5,10,20,50], device='cpu')

    # 6. Plot
    plot_rewards(total_rewards, avg_rewards)

    # Save agent policy
    os.makedirs('models', exist_ok=True)
    torch.save(agent.policy.state_dict(), 'models/dqn_policy_data.pth')
    with open('models/rewards.pkl', 'wb') as f:
        pickle.dump({'rewards': total_rewards, 'avg': avg_rewards}, f)

    print('Done. Models saved in ./models')
