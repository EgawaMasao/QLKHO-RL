# RL-based Multi-Product Inventory Management với Explainable AI

Dự án nghiên cứu áp dụng Reinforcement Learning (DQN, A2C) để tối ưu hóa quyết định tái nhập kho (replenishment) trong chuỗi cung ứng siêu thị đa sản phẩm, kết hợp pipeline XAI gồm ba tầng: **RDX** (Reward Decomposition) + **MSX** (Minimal Set Extraction) + **SHAP** để giải thích quyết định của agent.

---

## Mục lục

1. [Tổng quan dự án](#1-tổng-quan-dự-án)
2. [Cài đặt môi trường](#2-cài-đặt-môi-trường)
3. [Cấu trúc dự án](#3-cấu-trúc-dự-án)
4. [Kiến trúc hệ thống](#4-kiến-trúc-hệ-thống)
5. [Hướng dẫn chạy: Chuẩn bị dữ liệu](#5-hướng-dẫn-chạy-chuẩn-bị-dữ-liệu)
6. [Hướng dẫn chạy: Training](#6-hướng-dẫn-chạy-training)
7. [Hướng dẫn chạy: Prediction](#7-hướng-dẫn-chạy-prediction)
8. [Hướng dẫn chạy: Đánh giá XAI](#8-hướng-dẫn-chạy-đánh-giá-xai)
9. [Các Notebook và vai trò](#9-các-notebook-và-vai-trò)
10. [Checkpoints có sẵn](#10-checkpoints-có-sẵn)
11. [Metrics đánh giá](#11-metrics-đánh-giá)
12. [Kết quả nghiên cứu](#12-kết-quả-nghiên-cứu)

---

## 1. Tổng quan dự án

### Bài toán

Quản lý hàng tồn kho đa sản phẩm (**220 SKU**) trong siêu thị. Agent học chính sách tái nhập kho để cân bằng đồng thời bốn mục tiêu:

| Mục tiêu | Ký hiệu | Mô tả |
|---|---|---|
| Tránh hết hàng | `stockout` | Không để cạn kho gây mất doanh thu |
| Giảm tồn thừa | `overstock` | Không tích trữ quá mức gây đọng vốn |
| Giảm hao phí | `waste` | Giảm hàng hết hạn / hỏng hóc |
| Cân bằng tồn kho | `quantile_penalty` | Tối thiểu hóa bất đối xứng tồn kho giữa các SKU |

**Hàm reward:** `r = 1 - stockout - overstock - waste - quantile_penalty`

### Phương pháp

- **Thuật toán RL:** A2C_mod (training chính); DQN (so sánh)
- **Pipeline XAI:** RDX → MSX → SHAP (3 tầng bổ sung lẫn nhau)
- **Dữ liệu:** Instacart Grocery Dataset 2017 (Kaggle), 220 sản phẩm
- **Đánh giá:** Ablation study qua 5 seed, 3 kịch bản (EASY/MEDIUM/HARD), λ ∈ {0.5, 1.0, 1.5, 2.0}

---

## 2. Cài đặt môi trường

### Yêu cầu

- Python 3.9+
- TensorFlow 2.x
- SHAP, pandas, numpy, matplotlib, scikit-learn

### Kích hoạt môi trường ảo

```powershell
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Hoặc dùng cmd
.venv\Scripts\activate.bat
```

### Cài đặt thư viện

```bash
pip install tensorflow shap pandas numpy matplotlib scikit-learn
```

> **Lưu ý quan trọng:**
> - `inventory_management/training.py` (bản hiện tại) đã **loại bỏ `tensorflow_addons`** — dùng `tf.keras.layers.GroupNormalization` thay thế.
> - `file training/training.py` là bản **legacy** vẫn còn import `tensorflow_addons` — chỉ dùng để đọc checkpoint cũ.

---

## 3. Cấu trúc dự án

```
QLKHO-RL/
│
├── inventory_management/               # Module chính (Python scripts)
│   ├── prepare_data.py                 # Chuẩn bị dữ liệu TFRecord từ Instacart
│   ├── training.py                     # Training A2C/PPO + Prediction (không cần tfa)
│   ├── docs/                           # Tài liệu module
│   └── README.md                       # Mô tả gốc của module
│
├── Data/                               # Dữ liệu TFRecord (sẵn có)
│   ├── train.tfrecords                 # Dữ liệu training (timestep 0 → 1000)
│   ├── test.tfrecords                  # Dữ liệu test (timestep 1000 → cuối)
│   ├── capacity.tfrecords              # Sức chứa kệ hàng từng sản phẩm
│   ├── stock.tfrecords                 # Tồn kho ban đầu
│   └── data220/                        # (Legacy) TFRecord bản 220 sản phẩm cũ
│
├── checkpoints/                        # Toàn bộ checkpoint đã huấn luyện
│   ├── a2c/                            # Checkpoint A2C_mod
│   │   ├── checkpoints_220/            # A2C_mod 220 sản phẩm — CHECKPOINT CHÍNH
│   │   ├── checkpoints_a2c_42/         # Seed/hidden=42 — ablation
│   │   ├── checkpoints_a2c_123/        # Seed/hidden=123
│   │   ├── checkpoints_a2c_256/        # Seed/hidden=256
│   │   ├── checkpoints_a2c_512/        # Seed/hidden=512
│   │   └── checkpoints_a2c_1024/       # Seed/hidden=1024
│   └── dqn/                            # Checkpoint DQN
│       ├── checkpointDQN/              # DQN — CHECKPOINT CHÍNH
│       ├── checkpoints_dqn_comparison42/   # Seed=42 — so sánh 5 seeds
│       ├── checkpoints_dqn_comparison123/  # Seed=123
│       ├── checkpoints_dqn_comparison256/  # Seed=256
│       ├── checkpoints_dqn_comparison512/  # Seed=512
│       ├── checkpoints_dqn_comparison512_32/ # Seed=512, hidden=32
│       ├── checkpoints_dqn_comparison3/    # Seed=3
│       └── checkpoints_dqn_comparison3primary/ # Seed=3 (primary run)
│
├── notebooks/                          # Toàn bộ Jupyter notebook
│   ├── Data_analysis.ipynb             # EDA dataset Instacart
│   ├── training/                       # Notebook training
│   │   ├── A2C.ipynb                   # Training A2C gốc (self-contained)
│   │   ├── A2C-mod.ipynb               # Training A2C_mod (self-contained)
│   │   ├── A2C-mod-seed.ipynb          # Training A2C_mod qua 5 seeds
│   │   ├── dqn_a2c_comparison.ipynb    # So sánh DQN vs A2C vs Base-stock
│   │   └── training.py                 # Legacy training script (tensorflow_addons)
│   └── ablation/                       # Notebook ablation study
│       ├── ablation_study.ipynb        # Ablation tổng hợp RDX+MSX+SHAP (72 configs)
│       └── ablation_SHAP.ipynb         # Ablation SHAP hyperparameter
│
├── XAI/                                # Pipeline XAI
│   ├── marathon_data_4agents.pkl       # Dữ liệu marathon (4 agents)
│   ├── RDX/                            # Reward Decomposition
│   │   └── MSX/                        # Minimal Set Extraction
│   │       ├── RDX-MSX2.ipynb          # RDX + MSX đầy đủ — ENTRY POINT XAI CHÍNH
│   │       └── faithfulness_test_RDX_MSX.ipynb  # Faithfulness test RDX+MSX
│   └── SHAP/                           # Feature Attribution SHAP
│       ├── SHAP.ipynb                  # SHAP macro-level (3 feature groups)
│       ├── topk_shap_analysis.ipynb    # SHAP micro-level Top-20 trên 660 chiều
│       ├── ablation_SHAP.ipynb         # Ablation SHAP hyperparameter
│       ├── ablation_RDX.ipynb          # Ablation RDX theo λ, hidden_size
│       ├── shap_faithfulness_test.ipynb             # Faithfulness: MoRF/LeRF
│       ├── shap_faithfulness_random_baseline_test.ipynb  # Faithfulness: Random baseline
│       ├── combined_ablation_results.csv
│       ├── combined_summary_by_agent.csv
│       ├── combined_summary_by_lambda.csv
│       ├── combined_summary_detailed.csv
│       ├── combined_summary_table.csv
│       ├── fcs_grid_results_496states.csv
│       ├── fcs_summary_results.csv
│       └── topk_shap_full_results_660.csv
│
├── results/                            # Kết quả thực nghiệm
│   ├── ablation_results.csv            # Kết quả ablation: OCS, FCS, CAS, Stability, MSX_size
│   ├── ablation_results_fixed.csv      # Kết quả ablation (đã fix)
│   ├── faithfulness_results_rdx_msx.csv # Kết quả faithfulness test RDX+MSX
│   ├── raw_results_5seeds.csv          # Raw rewards qua 5 seeds (DQN vs A2C_mod)
│   ├── results_ci95.csv                # Kết quả tổng hợp với CI 95%
│   └── sensitivity_results.csv         # Sensitivity analysis theo λ
│
├── models/                             # Model weights đã lưu
│   ├── dqn_policy_data.pth             # DQN policy weights (PyTorch)
│   ├── q_table_demo.pkl                # Q-table demo
│   └── rewards.pkl                     # Lịch sử rewards
│
├── outputs/                            # Output runs
│   └── outputA2Cmod/                   # Output A2C_mod runs
│
└── CLAUDE.md                           # Hướng dẫn cho Claude Code
```

---

## 4. Kiến trúc hệ thống

### 4.1 Môi trường RL

| Thành phần | Mô tả |
|---|---|
| **State** | `[220, 3]` — `[x_norm, sales_norm, waste_est]`, tất cả ∈ [0,1] |
| **State tổng** | 660 chiều = 220 sản phẩm × 3 đặc trưng |
| **Action space** | 14 mức tái nhập kho: `[0, 0.005, 0.01, 0.0125, 0.015, 0.0175, 0.02, 0.03, 0.04, 0.08, 0.12, 0.2, 0.5, 1.0]` |
| **Transition** | `x' = clip(x + u, 0, 1) - sales`; waste giảm tồn kho 2.5%/chu kỳ |
| **Reward** | `r = 1 - stockout - overstock - waste - quantile_penalty` (additively separable) |

### 4.2 Mạng Neural (Actor-Critic)

**Actor (Policy Network):**
```
Input [220, 3]
  → Dense(hidden_size) → ReLU → Dropout(0.1)
  → Dense(hidden_size) → ReLU → Dropout(0.1)
  → Dense(hidden_size) → ReLU → Dropout(0.1)
  → Dense(14) → Softmax
Output: [220, 14]  — phân phối xác suất 14 hành động cho mỗi sản phẩm
```

**Critic (Value Network):**
```
Input [220, 3]
  → Dense(hidden_size) → GroupNorm(1) → ReLU → Dropout(0.1)
  → Dense(1) → Squeeze
Output: [220]  — giá trị trạng thái cho mỗi sản phẩm
```

**Hyperparameter đã thử nghiệm:**

| Tham số | Mặc định | Đã thử | Checkpoint tương ứng |
|---|---|---|---|
| `hidden_size` | 32 | 42, 123, 256, 512, 1024 | `checkpoints_a2c_<hidden>/` |
| `gamma` | 0.99 | — | — |
| `actor_lr` | 0.001 | — | — |
| `critic_lr` | 0.001 | — | — |
| `dropout` | 0.1 | — | — |
| `waste` | 0.025 | 0.05, 0.10, 0.20 | — |
| `num_products` | 220 | — | `checkpoints_220/` |

### 4.3 Pipeline XAI (3 tầng)

```
Quyết định Agent
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│  Tầng 1: RDX — Reward Decomposition eXplanation            │
│  ΔQ^k = γ[r^k(s, s'_best) - r^k(s, s'_alt)]               │
│  Phân rã reward thành 4 kênh:                              │
│    stockout | overstock | waste | quantile_penalty          │
│  → Model-agnostic, dùng ground-truth reward function        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Tầng 2: MSX — Minimal Set eXtraction                      │
│  Tìm tập con mục tiêu nhỏ nhất đủ giải thích quyết định    │
│  Ngưỡng λ ∈ {0.5, 1.0, 1.5, 2.0}                          │
│  Độ ổn định: Jaccard similarity qua nhiều giá trị λ         │
│  XAI configs: RDX_only | SHAP_only | Combined               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Tầng 3: SHAP — Feature Attribution                        │
│  Macro-level: 3 nhóm (Inventory, Sales/Demand, Waste)      │
│  Micro-level: Top-20 trên 660 chiều (220 SKU × 3)          │
│  Kernel SHAP + Empirical Synthetic Background (100 samples) │
│  Faithfulness: MoRF/LeRF + Random Masking Baseline         │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Hướng dẫn chạy: Chuẩn bị dữ liệu

> **Lưu ý:** Dữ liệu 220 sản phẩm đã được chuẩn bị sẵn tại `Data/`. Bỏ qua bước này nếu dùng data có sẵn.

### Bước 1: Tải dữ liệu Instacart

Tải dataset từ Kaggle: `https://www.kaggle.com/c/instacart-market-basket-analysis/data`

Giải nén vào thư mục `data/`. Cần 5 file:
```
data/orders.csv
data/products.csv
data/departments.csv
data/order_products__prior.csv
data/order_products__train.csv
```

### Bước 2: Chạy prepare_data.py

```bash
cd inventory_management

python prepare_data.py \
  --number_of_products 220 \
  --top_products 0.2 \
  --start_date 2017-01-01 \
  --end_date 2017-01-06 \
  --start_time_period 0 \
  --middle_time_period 1000 \
  --end_time_period -1 \
  --train_tfrecords_file ../Data/train.tfrecords \
  --test_tfrecords_file ../Data/test.tfrecords \
  --capacity_tfrecords_file ../Data/capacity.tfrecords \
  --stock_tfrecords_file ../Data/stock.tfrecords
```

**Tham số quan trọng:**

| Tham số | Mặc định | Mô tả |
|---|---|---|
| `--number_of_products` | 100 | Số sản phẩm — dùng **220** cho đúng với checkpoint |
| `--top_products` | 0.2 | Top 20% sản phẩm phổ biến nhất |
| `--middle_time_period` | 1000 | Mốc chia train/test (timestep) |
| `--end_time_period` | -1 | Kết thúc test (-1 = hết dữ liệu) |

**Output:** 4 file TFRecord tại `Data/`:
- `train.tfrecords` — dữ liệu training (timestep 0 → 1000)
- `test.tfrecords` — dữ liệu test (timestep 1000 → cuối)
- `capacity.tfrecords` — sức chứa kệ hàng từng sản phẩm
- `stock.tfrecords` — tồn kho ban đầu (ngẫu nhiên)

---

## 6. Hướng dẫn chạy: Training

### Training A2C_mod (khuyến nghị)

```bash
cd inventory_management

python training.py \
  --action TRAIN \
  --train_file ../Data/train.tfrecords \
  --capacity_file ../Data/capacity.tfrecords \
  --output_dir ../checkpoints/a2c/checkpoints_a2c_42 \
  --algorithm A2C_mod \
  --train_episodes 1000 \
  --num_products 220 \
  --hidden_size 32
```

### Training DQN (qua notebook)

Dùng `notebooks/training/dqn_a2c_comparison.ipynb` — đã tích hợp training DQN và so sánh với A2C + Base-stock policy.

### Tất cả tham số training

| Tham số | Mặc định | Lựa chọn | Mô tả |
|---|---|---|---|
| `--algorithm` | A2C | `A2C`, `A2C_mod`, `PPO` | Thuật toán học |
| `--hidden_size` | 32 | 42, 123, 256, 512, 1024 | Kích thước hidden layer |
| `--train_episodes` | 1000 | — | Số episode huấn luyện |
| `--num_products` | 100 | **220** | Số sản phẩm (phải khớp data) |
| `--gamma` | 0.99 | — | Discount factor |
| `--waste` | 0.025 | 0.05, 0.10, 0.20 | Tỷ lệ hao phí/chu kỳ |
| `--batch_size` | 32 | — | Kích thước batch |
| `--actor_learning_rate` | 0.001 | — | LR cho Actor |
| `--critic_learning_rate` | 0.001 | — | LR cho Critic |

**Naming convention checkpoint:** `checkpoints/<algorithm>/checkpoints_<algorithm>_<seed_or_hidden>/`
- A2C_mod: `checkpoints/a2c/checkpoints_a2c_42/`, `checkpoints/a2c/checkpoints_a2c_256/`, ...
- DQN: `checkpoints/dqn/checkpoints_dqn_comparison42/`, `checkpoints/dqn/checkpoints_dqn_comparison256/`, ...

**Quan sát khi training (stderr log):**
```
rewards: <step> <episode_len> <mean_reward>       → kỳ vọng tăng dần → ~0.7–0.9
stockouts: <step> <ep_len> <mean_stockout>        → giảm về ~0
waste: <step> <ep_len> <mean_waste>               → ổn định ở ~0.01–0.025
u: <step> <ep_len> <mean_action>                  → xấp xỉ mean sales khi hội tụ
```

Checkpoint tự động save mỗi 10 episode vào `<output_dir>/ckpt-XX`.

---

## 7. Hướng dẫn chạy: Prediction

```bash
cd inventory_management

python training.py \
  --action PREDICT \
  --output_dir ../checkpoints/a2c/checkpoints_220 \
  --capacity_file ../Data/capacity.tfrecords \
  --predict_file ../Data/test.tfrecords \
  --stock_file ../Data/stock.tfrecords \
  --output_file predictions.csv \
  --num_products 220
```

**Output** (`predictions.csv`): Mỗi timestep ghi 6 dòng:
```
stock:    <tồn kho đầu chu kỳ — 220 giá trị>
action:   <lượng tái nhập kho — 220 giá trị>
overstock:<lượng tràn kho — 220 giá trị>
sales:    <doanh số thực — 220 giá trị>
stockout: <lượng hết hàng — 220 giá trị>
capacity: <sức chứa chuẩn hóa — 220 giá trị>
```

---

## 8. Hướng dẫn chạy: Đánh giá XAI

Pipeline XAI có hai entry point chính: `XAI/RDX/MSX/RDX-MSX2.ipynb` (RDX+MSX) và `notebooks/ablation/ablation_study.ipynb` (tổng hợp).

---

### 8.1 RDX + MSX — Core XAI (entry point chính)

**File:** `XAI/RDX/MSX/RDX-MSX2.ipynb`

Notebook thực hiện toàn bộ pipeline RDX + MSX:

1. **Load models** — Load A2C_mod từ `checkpoints/a2c/checkpoints_220/` và DQN từ `checkpoints/dqn/checkpointDQN/`
2. **RDX** — Tính `ΔQ^k` cho 4 kênh reward bằng counterfactual simulation
3. **MSX** — Tìm minimal subset mục tiêu với λ ∈ {0.5, 1.0, 1.5, 2.0}
4. **Ablation** — So sánh xai_config: `RDX_only` | `SHAP_only` | `Combined`
5. **Export** → `results/ablation_results.csv`, `results/sensitivity_results.csv`

```python
# Cấu hình chính trong notebook
NUM_PRODUCTS = 220
NUM_FEATURES = 660          # = 220 × 3
NUM_ACTIONS = 14
LAMBDA_LIST = [0.5, 1.0, 1.5, 2.0]
SCENARIOS = ['EASY', 'MEDIUM', 'HARD']
```

**Cách chạy:** `Jupyter Notebook → Mở XAI/RDX/MSX/RDX-MSX2.ipynb → Run All`

---

### 8.2 Faithfulness Test RDX + MSX

**File:** `XAI/RDX/MSX/faithfulness_test_RDX_MSX.ipynb`

Kiểm định tính trung thực của RDX+MSX bằng can thiệp nhân quả — che đi từng thành phần reward và đo xem quyết định agent có thay đổi không.

**Output:** `results/faithfulness_results_rdx_msx.csv`

---

### 8.3 Ablation Study tổng hợp (RDX + MSX + SHAP)

**File:** `notebooks/ablation/ablation_study.ipynb`

Notebook tổng hợp chạy toàn bộ ablation grid:
- 2 agents × 3 scenarios × 4 λ × 3 xai_configs = 72 cấu hình
- Tính đầy đủ OCS, FCS, CAS, Stability, MSX_size
- Export ra `results/ablation_results_fixed.csv`

**Cách chạy:** `Jupyter Notebook → Mở notebooks/ablation/ablation_study.ipynb → Run All`

---

### 8.4 SHAP Macro-level (3 nhóm đặc trưng)

**File:** `XAI/SHAP/SHAP.ipynb`

Phân tích SHAP trên 3 nhóm tổng hợp (Inventory, Sales, Waste) với Kernel SHAP:

```python
# Cấu hình Background Distribution (100 samples)
# Inventory, Sales: Uniform(0, capacity_max)
# Waste = 0.025 × Inventory + N(0, σ²)   ← bảo toàn tương quan vật lý
```

---

### 8.5 SHAP Micro-level Top-k (660 chiều)

**File:** `XAI/SHAP/topk_shap_analysis.ipynb`

Phân tích SHAP trên toàn bộ không gian 660 chiều để tìm Top-20 SKU ảnh hưởng nhất:

```python
TOP_K = 20
AGENTS = ['DQN', 'A2C_mod']
SCENARIOS = ['EASY', 'MEDIUM', 'HARD']
```

Kết quả phân tách theo màu: Xanh dương = Inventory | Xanh lá = Demand | Đỏ = Waste.

---

### 8.6 Faithfulness Test SHAP (MoRF/LeRF + Random Baseline)

| File | Nội dung |
|---|---|
| `XAI/SHAP/shap_faithfulness_test.ipynb` | MoRF/LeRF perturbation — xác nhận SHAP nhân quả |
| `XAI/SHAP/shap_faithfulness_random_baseline_test.ipynb` | Random masking (B=30 Monte Carlo) — bác bỏ giả thuyết "nhạy cảm ngẫu nhiên" |

**Bất đẳng thức cần thỏa mãn:**
```
Drop_MoRF (SHAP-guided) > Drop_Random (B=30) > Drop_LeRF (SHAP-guided)
```

---

### 8.7 So sánh DQN vs A2C vs Base-stock

**File:** `notebooks/training/dqn_a2c_comparison.ipynb`

So sánh toàn diện ba chính sách:
- **DQN** — Value-based (Q-network)
- **A2C_mod** — Policy-based (Actor-Critic)
- **Base-stock** — Heuristic kinh điển (baseline so sánh)

---

## 9. Các Notebook và vai trò

| Notebook | Thư mục | Vai trò |
|---|---|---|
| `RDX-MSX2.ipynb` | `XAI/RDX/MSX/` | **Entry point XAI chính**: RDX + MSX đầy đủ |
| `faithfulness_test_RDX_MSX.ipynb` | `XAI/RDX/MSX/` | Faithfulness test cho RDX + MSX |
| `SHAP.ipynb` | `XAI/SHAP/` | SHAP macro-level (3 feature groups) |
| `topk_shap_analysis.ipynb` | `XAI/SHAP/` | SHAP micro-level Top-20 trên 660 chiều |
| `ablation_SHAP.ipynb` | `XAI/SHAP/` | Ablation SHAP hyperparameter |
| `ablation_RDX.ipynb` | `XAI/SHAP/` | Ablation RDX theo λ, hidden_size |
| `shap_faithfulness_test.ipynb` | `XAI/SHAP/` | Faithfulness SHAP: MoRF/LeRF |
| `shap_faithfulness_random_baseline_test.ipynb` | `XAI/SHAP/` | Faithfulness SHAP: Random masking baseline |
| `ablation_study.ipynb` | `notebooks/ablation/` | Ablation tổng hợp: RDX+MSX+SHAP, 72 cấu hình |
| `ablation_SHAP.ipynb` | `notebooks/ablation/` | Ablation SHAP (bản notebook) |
| `dqn_a2c_comparison.ipynb` | `notebooks/training/` | So sánh DQN vs A2C vs Base-stock + training DQN |
| `A2C-mod.ipynb` | `notebooks/training/` | Training A2C_mod (self-contained, seed cố định) |
| `A2C.ipynb` | `notebooks/training/` | Training A2C gốc (self-contained) |
| `A2C-mod-seed.ipynb` | `notebooks/training/` | Training A2C_mod qua 5 seeds |
| `Data_analysis.ipynb` | `notebooks/` | EDA dataset Instacart |

---

## 10. Checkpoints có sẵn

### A2C (`checkpoints/a2c/`)

| Thư mục | Agent | Mô tả |
|---|---|---|
| `checkpoints/a2c/checkpoints_220/` | A2C_mod | **Checkpoint chính** — 220 sản phẩm, training đầy đủ |
| `checkpoints/a2c/checkpoints_a2c_42/` | A2C_mod | Seed/hidden=42 — dùng cho ablation |
| `checkpoints/a2c/checkpoints_a2c_123/` | A2C_mod | Seed/hidden=123 |
| `checkpoints/a2c/checkpoints_a2c_256/` | A2C_mod | Seed/hidden=256 |
| `checkpoints/a2c/checkpoints_a2c_512/` | A2C_mod | Seed/hidden=512 |
| `checkpoints/a2c/checkpoints_a2c_1024/` | A2C_mod | Seed/hidden=1024 |

### DQN (`checkpoints/dqn/`)

| Thư mục | Agent | Mô tả |
|---|---|---|
| `checkpoints/dqn/checkpointDQN/` | DQN | **Checkpoint DQN chính** |
| `checkpoints/dqn/checkpoints_dqn_comparison42/` | DQN | Seed=42 — dùng cho so sánh 5 seeds |
| `checkpoints/dqn/checkpoints_dqn_comparison123/` | DQN | Seed=123 |
| `checkpoints/dqn/checkpoints_dqn_comparison256/` | DQN | Seed=256 |
| `checkpoints/dqn/checkpoints_dqn_comparison512/` | DQN | Seed=512 |
| `checkpoints/dqn/checkpoints_dqn_comparison512_32/` | DQN | Seed=512, hidden=32 |
| `checkpoints/dqn/checkpoints_dqn_comparison3/` | DQN | Seed=3 |
| `checkpoints/dqn/checkpoints_dqn_comparison3primary/` | DQN | Seed=3 (primary run) |

> **Lưu ý khi load checkpoint DQN:** File `notebooks/training/training.py` dùng `tensorflow_addons`. Nếu không cài tfa, load DQN qua notebook `notebooks/training/dqn_a2c_comparison.ipynb` (đã xử lý compat).

---

## 11. Metrics đánh giá

### Metrics XAI (từ `results/ablation_results.csv`)

| Metric | Tên đầy đủ | Ý nghĩa |
|---|---|---|
| **OCS** | Objective Coverage Score | Tỷ lệ mục tiêu reward có đóng góp ≥ ngưỡng |
| **MSX_size** | Minimal Set Size | Số mục tiêu tối thiểu để giải thích đầy đủ |
| **Stability** | Jaccard Stability | Độ ổn định MSX qua các giá trị λ |
| **FCS** | Feature Coverage Score | Tỷ lệ đặc trưng SHAP có |φ| ≥ ngưỡng |
| **CAS** | Cross-domain Alignment Score | Jaccard(SHAP features, RDX objectives) |

### Metrics Faithfulness (từ `results/faithfulness_results_rdx_msx.csv`)

| Metric | Mô tả |
|---|---|
| **ΔQ** | Sụt giảm Q-value sau khi che k feature (DQN) |
| **Δπ** | Sụt giảm xác suất action tối ưu (A2C_mod) |
| **ASR** | Action Switching Rate — % trạng thái bị đổi quyết định |

### Metrics RL (từ `results/results_ci95.csv`)

| Metric | Mô tả |
|---|---|
| **Total Reward** | Tổng reward trung bình (mean ± CI95, N=5 seeds) |
| **Service Reward** | Thành phần tránh stockout |
| **Holding Cost** | Thành phần penalize overstock |
| **Waste Cost** | Thành phần penalize hao phí |
| **Order Cost** | Thành phần penalize đặt hàng nhiều |

### SHAP Micro-level

$$I_{Micro}(f_j) = \frac{1}{N \cdot A} \sum_{n=1}^{N} \sum_{a=1}^{A} |\phi_{j,a}^{(n)}|$$



### Tài liệu tham khảo

1. *Scalable multi-product inventory control with lead time constraints using RL* — Neural Computing and Applications 2021
2. *Using RL for a Large Variable-Dimensional Inventory Management Problem* — ALA 2020 ([PDF](https://ala2020.vub.ac.be/papers/ALA2020_paper_5.pdf))
3. *RL for Multi-Product Multi-Node Inventory Management in Supply Chains* — arXiv:2006.04037
