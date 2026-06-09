# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Reinforcement learning research project for **multi-product inventory management** with explainable AI (XAI). Trains DQN and A2C agents to optimize replenishment decisions for grocery store inventory, then explains decisions via novel RDX (Reward Decomposition) + MSX (Minimal Set Extraction) + SHAP pipeline.

## Environment Setup

```powershell
# Activate virtual environment
.venv\Scripts\activate

# Install dependencies (TF2, SHAP, pandas, matplotlib)
pip install -r requirements.txt  # if present, otherwise install manually
```

## Common Commands

### Data Preparation

```bash
python inventory_management/prepare_data.py \
  --number_of_products 100 \
  --top_products 0.2 \
  --start_date 2017-01-01 \
  --end_date 2017-01-06
```

Outputs TFRecord files to `data/`: `train.tfrecords`, `test.tfrecords`, `capacity.tfrecords`, `stock.tfrecords`.

### Training

```bash
python inventory_management/training.py \
  --train_file data/train.tfrecords \
  --capacity_file data/capacity.tfrecords \
  --output_dir checkpoints_a2c_42 \
  --algorithm A2C \
  --train_episodes 1000 \
  --num_products 100 \
  --hidden_size 256
```

Supported `--algorithm` values: `A2C`, `A2C_mod`, `PPO`.

### Inference / Prediction

```bash
python inventory_management/training.py \
  --action PREDICT \
  --output_dir checkpoints_a2c_42 \
  --predict_file data/test.tfrecords \
  --output_file predictions.csv
```

## Architecture

### RL Environment

- **State:** `[num_products, 3]` — `[normalized_inventory, forecasted_sales, waste_estimate]`, all in `[0, 1]`
- **Action space:** 14 discrete replenishment fractions `[0, 0.005, 0.01, ..., 1.0]`
- **Reward:** `r = 1 - stockout - overstock - waste - quantile_penalty` (additively separable — critical for RDX)
- **Transition:** `x_next = clip(x + u, 0, 1) - sales`; waste decays inventory at 2.5%/period

### Neural Networks (Actor-Critic)

- **Actor (policy):** 4-layer dense → softmax over 14 actions
- **Critic (value):** 2-layer dense → scalar state value
- Dropout 0.1; GroupNormalization via Keras (removed `tensorflow_addons` dependency)
- Key hyperparameter: `hidden_size` (tested: 42, 123, 256, 512, 1024)

### XAI Pipeline

Three complementary methods combined:

1. **RDX (Reward Decomposition):** Model-agnostic. Simulates counterfactual actions (best vs. alternative), decomposes reward difference into 4 objective channels: `ΔQ^k = γ[r^k(s, s'_best) - r^k(s, s'_alt)]`

2. **MSX (Minimal Set Extraction):** Finds the smallest subset of objectives that explains the decision. Controlled by threshold `λ` (tested: 0.5, 1.0, 1.5, 2.0). Stability measured via Jaccard similarity across λ values.

3. **SHAP:** `GradientExplainer` measuring which input features (inventory/sales/waste) drive policy outputs.

**Key justification:** RDX uses the ground-truth reward function directly (not Q-network approximations), making it architecture-agnostic and suitable for cross-model comparison (DQN vs A2C).

### Evaluation Metrics

| Metric | Description |
|--------|-------------|
| OCS | Objective Coverage Score — fraction of objectives meaningfully used |
| MSX_size | Min number of objectives for full explanation |
| FCS | Feature Coverage Score — fraction of features used meaningfully |
| CAS | Cross-domain Alignment Score — Jaccard(SHAP features, RDX objectives) |

All reported with 95% CI over 5 random seeds.

## Key Files

| File | Role |
|------|------|
| `inventory_management/training.py` | Main TF2 training + prediction entrypoint |
| `inventory_management/prepare_data.py` | Instacart dataset → TFRecord pipeline |
| `training.py` | Legacy TF1 version (do not use for new work) |
| `ablation_study.ipynb` | Full ablation over λ, hidden_size, scenario difficulty |
| `ablation_SHAP.ipynb` | SHAP feature importance analysis |
| `dqn_a2c_comparison.ipynb` | Head-to-head DQN vs A2C evaluation |
| `statistical_analysis_CI95.ipynb` | CI95 significance tests over 5 seeds |
| `XAI/RDX-MSX.ipynb` | Core RDX+MSX explainability experiments |
| `RDX_approach_explanation.md` | Methodological justification for model-agnostic RDX |
| `XAI_Config_Analysis.md` | Summary of XAI evaluation results |

## Checkpoint Convention

Checkpoint folders follow the pattern `checkpoints_<algorithm>_<seed>/` (e.g., `checkpoints_a2c_42/`, `checkpoints_dqn_256/`). The `--output_dir` flag in training controls this.

## Data Note

Raw data is the Instacart grocery dataset. `prepare_data.py` selects top 20% most-ordered products from 12 departments and samples ~100 products for training. Sales forecasts are derived from order history; shelf capacity is set to 3–4 days of average sales.
