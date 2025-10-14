# 💾 Hướng dẫn Lưu và Tái sử dụng Q-Learning Model

## 📚 Tổng quan

File `test2.ipynb` đã được cải thiện với khả năng:
- ✅ **Lưu Q-table** sau khi huấn luyện
- ✅ **Load Q-table** đã lưu để tái sử dụng
- ✅ **Lưu metadata** (hyperparameters, training history)
- ✅ **Visualize learning curve** để đánh giá quá trình học

---

## 🚀 Cách sử dụng

### 🔹 Scenario 1: Train model mới lần đầu

1. **Mở notebook**: `test2.ipynb`
2. **Đặt cờ training**:
   ```python
   USE_PRETRAINED = False  # Cell 5
   ```
3. **Chạy tuần tự từ Cell 1 → Cell cuối**
4. **Kết quả**: 
   - Model được train và lưu vào `models/q_table_inventory.pkl`
   - Learning curve được vẽ ra
   - Q-table sẵn sàng để tái sử dụng

---

### 🔹 Scenario 2: Load model đã train (Khuyến nghị ⭐)

1. **Đảm bảo file model tồn tại**: `models/q_table_inventory.pkl`
2. **Đặt cờ load**:
   ```python
   USE_PRETRAINED = True  # Cell 5 (mặc định)
   ```
3. **Chạy Cell 1 → 5**:
   - Cell 1-2: Import libraries
   - Cell 3: Load parameters từ file
   - Cell 4: Định nghĩa môi trường
   - Cell 5: **Load Q-table đã lưu** ✅
4. **Skip Cell 6 (Training)** - không cần train lại!
5. **Chạy từ Cell 8 trở đi**: Evaluation và visualization

**⏱️ Thời gian tiết kiệm**: 
- Training mới: ~5-10 phút (1000 episodes)
- Load model: ~1 giây

---

## 📦 Cấu trúc file đã lưu

File `models/q_table_inventory.pkl` chứa:

```python
{
    'Q_table': numpy.ndarray (41 x 2),  # Q-values cho 41 states, 2 actions
    'params': {
        'alpha': 0.2,
        'gamma': 0.9,
        'epsilon': 0.1,
        'q': 6,
        'r': 3,
        # ... các tham số khác
    },
    'training_info': {
        'timestamp': "2025-10-14 10:30:45",
        'final_avg_cost': 2458.32,
        'episode_costs': [list of 1000 values],
        'episode_holding': [...],
        'episode_backorder': [...],
        'episode_ordering': [...]
    },
    'states': array([-20, -19, ..., 20]),
    'actions': [0, 1],
    'min_IP': -20,
    'max_IP': 20
}
```

---

## 🔧 API Functions

### `save_model(Q, params, training_info, filename)`

Lưu Q-table và metadata vào file pickle.

**Parameters:**
- `Q`: numpy array - Q-table đã train
- `params`: dict - Hyperparameters
- `training_info`: dict - Training history
- `filename`: str - Đường dẫn file (mặc định: `models/q_table_inventory.pkl`)

**Example:**
```python
save_model(Q, params, training_info, "models/q_table_v2.pkl")
```

---

### `load_model(filename)`

Load Q-table và metadata từ file.

**Returns:**
- `model_data`: dict hoặc `None` (nếu file không tồn tại)

**Example:**
```python
loaded = load_model("models/q_table_inventory.pkl")
if loaded:
    Q = loaded['Q_table']
    params = loaded['params']
```

---

## 📊 So sánh Performance

| Metric | Train mới | Load model |
|--------|-----------|------------|
| Thời gian | ~5-10 phút | ~1 giây |
| RAM usage | Cao | Thấp |
| Kết quả | Khác nhau (random) | Nhất quán |
| Use case | Research, tuning | Production, demo |

---

## 💡 Tips & Best Practices

### ✅ Khi nào nên train lại?

- Thay đổi hyperparameters (alpha, gamma, epsilon)
- Thay đổi chi phí (O, h, b)
- Thay đổi mô hình nhu cầu (mu, sigma)
- Muốn thử chiến lược khác (số episodes, epsilon decay)

### ✅ Khi nào dùng model đã lưu?

- Demo cho người khác
- Chạy evaluation/testing nhiều lần
- So sánh với baseline
- Deploy vào production

### ✅ Quản lý nhiều versions

Lưu model với tên khác nhau:
```python
save_model(Q, params, info, "models/q_table_alpha02_gamma09.pkl")
save_model(Q, params, info, "models/q_table_alpha05_gamma05.pkl")
```

### ✅ Backup training history

Training history (episode_costs, v.v.) cũng được lưu → có thể vẽ lại learning curve bất cứ lúc nào!

---

## 🐛 Troubleshooting

### ❌ Error: "File không tồn tại"

**Nguyên nhân**: Chưa train model lần nào.

**Giải pháp**: 
```python
USE_PRETRAINED = False  # Train mới
```

### ❌ Error: "Q_table shape không khớp"

**Nguyên nhân**: Thay đổi `min_IP` hoặc `max_IP` sau khi lưu model.

**Giải pháp**: Train lại model với config mới.

### ❌ Muốn xóa model cũ và train lại

```python
import os
if os.path.exists("models/q_table_inventory.pkl"):
    os.remove("models/q_table_inventory.pkl")
    print("Đã xóa model cũ")
```

---

## 📈 Ví dụ Workflow

### Workflow nghiên cứu (Research)

```
1. Thử nghiệm alpha = 0.2, gamma = 0.9
   → Train → Lưu "q_table_v1.pkl"
   
2. Thử nghiệm alpha = 0.5, gamma = 0.5
   → Train → Lưu "q_table_v2.pkl"
   
3. So sánh performance:
   - Load v1 → Evaluate
   - Load v2 → Evaluate
   - Chọn model tốt nhất
```

### Workflow production

```
1. Train model tốt nhất trên máy dev
   → Lưu "q_table_production.pkl"
   
2. Copy file .pkl sang server
   
3. Server chỉ cần:
   - Load model
   - Chạy evaluation/inference
   - Không cần train lại!
```

---

## 📚 Tham khảo

- **Paper**: Q-Learning for Inventory Management (xem `README.md`)
- **Code gốc**: `test.ipynb`
- **Code cải tiến**: `test2.ipynb` ← File này

---

## ✨ Tính năng mới đã thêm

1. ✅ **Cell 2**: Import pickle, os, datetime
2. ✅ **Cell 5-6**: Load model function + auto-load logic
3. ✅ **Cell 7**: Save model function (sau training)
4. ✅ **Cell 9**: Learning curve visualization
5. ✅ **Thư mục models/**: Chứa các file .pkl

---

**Tác giả**: GitHub Copilot  
**Ngày cập nhật**: 2025-10-14  
**Version**: 2.0 (với model persistence)
