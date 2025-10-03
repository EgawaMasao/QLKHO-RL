
import math
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque, namedtuple
import random
import os
import pickle

# ---------------- Môi trường ( trả về chi phí cho mỗi SKU) ----------------
class MultiSKUInventoryEnvV2:
    def __init__(self, N_SKU=1000, lead_time=2, horizon=90, sku_mu=None, seed=0):
        self.N = N_SKU
        self.lead_time = lead_time
        self.horizon = horizon
        np.random.seed(seed)
        if sku_mu is None:
            base = np.concatenate([np.random.uniform(0.01, 5, size=self.N//2),
                                   np.random.uniform(5, 100, size=self.N - self.N//2)])
            sku_mu = base
        self.sku_mu = np.array(sku_mu)
        self.sku_sigma = np.sqrt(self.sku_mu)
        self.reset()

    def reset(self):
        self.I = np.maximum(0, np.round(1.5 * self.sku_mu * self.lead_time).astype(int))
        self.oo = np.zeros((self.N, self.lead_time), dtype=int)
        self.backlog = np.zeros(self.N, dtype=int)
        self.promo = (np.random.rand(self.N) < 0.05).astype(int)
        self.t = 0
        return self._get_full_state()

    def step(self, orders):
        assert len(orders) == self.N
        # các tham số chi phí (mỗi SKU)
        holding_cost_per_unit = 0.01
        stockout_cost_per_unit = 1.0
        order_fixed_cost = 0.5
        order_unit_cost = 0.0

        # Đặt những hàng được order sau đó vào cuối bucket
        self.oo[:, -1] += orders

        promo_multiplier = 1.5
        demand_lambda = self.sku_mu * (1 + (self.promo * (promo_multiplier - 1)))
        demand = np.random.poisson(demand_lambda).astype(int)

        # phục vụ nhu cầu: ưu tiên backlog trước
        available = self.I.copy()
        served = np.minimum(available, demand + self.backlog)
        serve_backlog = np.minimum(self.backlog, served)
        self.backlog -= serve_backlog
        served_new = served - serve_backlog
        unfilled = (demand - served_new)
        self.backlog += np.maximum(0, unfilled)
        # Hàng mua thành công thì giảm bớt số hàng hiện có
        self.I -= (served_new + serve_backlog)

        # arrivals
        arrivals = self.oo[:, 0].copy()
        if self.lead_time > 1:
            self.oo[:, :-1] = self.oo[:, 1:]
        self.oo[:, -1] = 0
        self.I += arrivals

        # chi phí SKU (vector)
        holding_cost = holding_cost_per_unit * self.I  # per SKU
        stockout_cost = stockout_cost_per_unit * self.backlog
        order_cost = order_fixed_cost * (orders > 0).astype(float) + order_unit_cost * orders
        # mỗi sku reward = -(holding + stockout + order)
        reward_per_sku = -(holding_cost + stockout_cost + order_cost)
        total_reward = reward_per_sku.sum()

        self.t += 1
        done = (self.t >= self.horizon)
        return self._get_full_state(), reward_per_sku, done, {"demand": demand, "arrivals": arrivals}

    def _get_full_state(self):
        return {
            "I": self.I.copy(),
            "oo": self.oo.copy(),
            "backlog": self.backlog.copy(),
            "promo": self.promo.copy(),
            "mu": self.sku_mu.copy(),
            "sigma": self.sku_sigma.copy(),
            "t": self.t
        }

# ---------------- Feature extractor (per-sku vector) ----------------
def sku_feature_vector(state, idx, lead_time=2):
    I = float(state["I"][idx])
    oo = state["oo"][idx]
    backlog = float(state["backlog"][idx])
    promo = float(state["promo"][idx])
    mu = float(state["mu"][idx])
    sigma = float(state["sigma"][idx])
    t = state["t"]

    IP = I + oo.sum() - backlog
    oo_due1 = float(oo[0]) if lead_time >= 1 else 0.0
    oo_other = float(max(0, oo.sum() - oo_due1))
    sigma_L = math.sqrt(max(1e-6, mu * max(1, lead_time)))

    # normalized features
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

# ---------------- DQN network & agent ----------------
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

Transition = namedtuple('Transition', ('state', 'action', 'reward', 'next_state', 'done'))

class ReplayBuffer:
    def __init__(self, capacity=200000):
        self.buffer = deque(maxlen=capacity)
    def push(self, *args):
        self.buffer.append(Transition(*args))
    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        return Transition(*zip(*batch))
    def __len__(self): return len(self.buffer)

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
    def act(self, state_batch, eps=0.1):
        # state_batch: np.array (B, input_dim)
        if np.random.rand() < eps:
            return np.random.randint(self.n_actions)
        st = torch.tensor(state_batch, dtype=torch.float32, device=self.device)
        with torch.no_grad():
            q = self.policy(st)
            return int(torch.argmax(q, dim=1).cpu().numpy()[0])
    def q_values(self, states):
        st = torch.tensor(states, dtype=torch.float32, device=self.device)
        return self.policy(st)
    def update(self, transitions, batch_size=64, tau=1e-3):
        if len(transitions) < batch_size:
            return
        b = transitions.sample(batch_size)
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

        # soft update target
        for p, tp in zip(self.policy.parameters(), self.target.parameters()):
            tp.data.copy_(tau * p.data + (1 - tau) * tp.data)

# ---------------- Training loop ----------------
def train_dqn_demo(n_sku=2000, episodes=50, horizon=60, device='cpu'):
    env = MultiSKUInventoryEnvV2(N_SKU=n_sku, lead_time=2, horizon=horizon)
    n_actions = 7
    action_buckets = np.array([0,1,2,5,10,20,50], dtype=int)
    input_dim = 10  # as built by sku_feature_vector
    agent = DQNAgent(input_dim, n_actions, lr=1e-3, gamma=0.99, device=device)
    buffer = ReplayBuffer(capacity=200000)

    eps_start = 0.5
    eps_end = 0.02
    eps_decay = episodes * n_sku * horizon / 20.0  # heuristic

    # training
    total_rewards = []
    for ep in range(episodes):
        state = env.reset()
        ep_reward = 0.0
        done = False
        while not done:
            # for scalability: sample subset of SKUs to take actions this step (mini-batch)
            # here sample M SKUs to act on and use network to pick action for each
            M = min(256, env.N)  # batch size per step
            skus = np.random.choice(env.N, size=M, replace=False)

            feats = np.stack([sku_feature_vector(state, s, lead_time=env.lead_time) for s in skus])
            # epsilon schedule
            ttotal = agent.steps
            eps = max(eps_end, eps_start - (eps_start - eps_end) * (ttotal / max(1, eps_decay)))
            with torch.no_grad():
                qvals = agent.q_values(feats).cpu().numpy()
            # choose actions per sku (epsilon-greedy per item)
            actions_idx = []
            for i in range(M):
                if np.random.rand() < eps:
                    actions_idx.append(np.random.randint(n_actions))
                else:
                    actions_idx.append(int(np.argmax(qvals[i])))
            # build full orders vector (scale buckets by mu)
            orders = np.zeros(env.N, dtype=int)
            for i, s in enumerate(skus):
                base = action_buckets[actions_idx[i]]
                scale = int(max(1, round(state["mu"][s] / 5.0)))
                orders[s] = int(base * scale)

            next_state, reward_per_sku, done, info = env.step(orders)
            ep_reward += reward_per_sku.sum()

            # push transitions per selected SKU to replay buffer
            for i, s in enumerate(skus):
                st_vec = feats[i]
                act = actions_idx[i]
                r = float(reward_per_sku[s])
                next_vec = sku_feature_vector(next_state, s, lead_time=env.lead_time)
                buffer.push(st_vec, act, r, next_vec, float(done))
            # update
            agent.update(buffer, batch_size=128, tau=0.005)
            agent.steps += 1
            state = next_state

        total_rewards.append(ep_reward)
        if (ep+1) % 5 == 0:
            avg = np.mean(total_rewards[-5:])
            print(f"Ep {ep+1}/{episodes} - avg reward (last5): {avg:.2f}, eps: {eps:.3f}, buffer_len: {len(buffer)}")

    # save models
    os.makedirs("models", exist_ok=True)
    torch.save(agent.policy.state_dict(), "models/dqn_policy.pth")
    with open("models/dqn_info.pkl", "wb") as f:
        pickle.dump({"rewards": total_rewards}, f)
    print("Training complete.")
    return agent, env, total_rewards

if __name__ == "__main__":
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    train_dqn_demo(n_sku=2000, episodes=20, horizon=60, device=device)
