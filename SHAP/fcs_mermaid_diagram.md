# FCS Analysis Summary

```mermaid
graph TB
    Start[SHAP-only Ablation Study]
    Start --> DQN[DQN Agent]
    Start --> A2C[A2C_mod Agent]
    
    DQN --> DQN_EASY[EASY Scenario]
    DQN --> DQN_MED[MEDIUM Scenario]
    DQN --> DQN_HARD[HARD Scenario]
    
    A2C --> A2C_EASY[EASY Scenario]
    A2C --> A2C_MED[MEDIUM Scenario]
    A2C --> A2C_HARD[HARD Scenario]
    DQN_EAS --> DQN_EAS_R[FCS: 66.7%<br/>Key Feature: Inventory]
    DQN_MED --> DQN_MED_R[FCS: 66.7%<br/>Key Feature: Sales]
    DQN_HAR --> DQN_HAR_R[FCS: 88.9%<br/>Key Feature: Sales]
    A2C_EAS --> A2C_EAS_R[FCS: 66.7%<br/>Key Feature: Inventory]
    A2C_MED --> A2C_MED_R[FCS: 66.7%<br/>Key Feature: Sales]
    A2C_HAR --> A2C_HAR_R[FCS: 66.7%<br/>Key Feature: Sales]

    style Start fill:#e1f5ff
    style DQN fill:#bbdefb
    style A2C fill:#f8bbd0
    style DQN_EASY fill:#c8e6c9
    style DQN_MED fill:#fff9c4
    style DQN_HARD fill:#ffccbc
    style A2C_EASY fill:#c8e6c9
    style A2C_MED fill:#fff9c4
    style A2C_HARD fill:#ffccbc
```


## Summary Table

| Agent | Scenario | Avg FCS | Most Important Feature |
|-------|----------|---------|------------------------|
| DQN | EASY | 66.7% | Inventory |
| DQN | MEDIUM | 66.7% | Sales |
| DQN | HARD | 88.9% | Sales |
| A2C_mod | EASY | 66.7% | Inventory |
| A2C_mod | MEDIUM | 66.7% | Sales |
| A2C_mod | HARD | 66.7% | Sales |
