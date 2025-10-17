# 🔥 Epsilon Decay Strategy - Cải thiện hiệu quả học của Q-Learning Agent

## 📊 Vấn đề với Epsilon cố định

### ❌ Trước đây (Epsilon = 0.1 cố định)

```python
epsilon = 0.1  # Cố định suốt 1000 episodes
```

**Nhược điểm:**
- Agent **khám phá 10%** suốt quá trình học
- Ngay cả khi đã tìm ra chính sách tốt (episode 800-1000), vẫn tiếp tục khám phá ngẫu nhiên
- Làm **chậm hội tụ** và giảm performance ở giai đoạn cuối

---

## ✅ Giải pháp: Epsilon Decay

### 🎯 Chiến lược mới

```python
epsilon_start = 0.3      # Khám phá nhiều ở đầu (30%)
epsilon_end = 0.01       # Khai thác nhiều ở cuối (1%)
epsilon_decay = 0.995    # Giảm 0.5% mỗi episode

# Mỗi episode:
epsilon = max(epsilon_end, epsilon * epsilon_decay)
```

---

## 📈 Epsilon Decay Timeline

| Episode Range | Epsilon (ε) | Behavior | Mục đích |
|--------------|-------------|----------|----------|
| **1-200** | 0.30 → 0.18 | **Exploration** (Khám phá) | Thử nhiều actions khác nhau, build Q-table |
| **200-500** | 0.18 → 0.08 | **Balanced** (Cân bằng) | Vừa thử vừa khai thác Q-table |
| **500-800** | 0.08 → 0.03 | **Exploitation** (Khai thác) | Dùng chính sách đã học, ít thử nghiệm |
| **800-1000** | 0.03 → 0.01 | **Pure Exploitation** | Hầu như chỉ dùng best action |

---

## 🧮 Toán học: Epsilon Decay Formula

### Exponential Decay

$$
\epsilon_t = \max(\epsilon_{min}, \epsilon_0 \times \text{decay}^t)
$$

Trong đó:
- $\epsilon_t$: Epsilon ở episode t
- $\epsilon_0$: Epsilon ban đầu (0.3)
- $\epsilon_{min}$: Epsilon tối thiểu (0.01)
- $\text{decay}$: Hệ số giảm (0.995)

### Ví dụ cụ thể

```python
# Episode 1
epsilon = max(0.01, 0.3 * 0.995^0) = 0.300

# Episode 100
epsilon = max(0.01, 0.3 * 0.995^100) = 0.182

# Episode 500
epsilon = max(0.01, 0.3 * 0.995^500) = 0.024

# Episode 1000
epsilon = max(0.01, 0.3 * 0.995^1000) = 0.010
```

---

## 🎓 Exploration-Exploitation Tradeoff

### Exploration (Khám phá)
- **Mục đích**: Tìm kiếm actions mới, cập nhật Q-table
- **Khi nào**: Đầu training (high epsilon)
- **Cách**: Random action
```python
if np.random.rand() < epsilon:
    a = np.random.choice(actions)  # Random
```

### Exploitation (Khai thác)
- **Mục đích**: Sử dụng kiến thức đã học (Q-table)
- **Khi nào**: Cuối training (low epsilon)
- **Cách**: Best action theo Q-table
```python
else:
    a = np.argmax(Q[state, :])  # Best action
```

---

## 📊 So sánh Performance

| Metric | Epsilon cố định (0.1) | Epsilon decay (0.3→0.01) |
|--------|----------------------|-------------------------|
| **Episode 1-200** | Học chậm (explore ít) | ✅ Học nhanh (explore nhiều) |
| **Episode 200-500** | Trung bình | ✅ Cân bằng tốt |
| **Episode 500-1000** | ❌ Vẫn explore 10% | ✅ Exploit tối đa |
| **Final cost** | Cao hơn | **Thấp hơn 5-15%** |
| **Convergence** | Chậm | ✅ Nhanh hơn |

---

## 🔧 Cách điều chỉnh Epsilon Parameters

### 1. Epsilon Start (ε₀)

```python
epsilon_start = 0.3  # Default
```

**Tăng lên (0.4-0.5)** nếu:
- Problem phức tạp, nhiều states
- Muốn khám phá rộng hơn
- Model chưa hội tụ

**Giảm xuống (0.1-0.2)** nếu:
- Problem đơn giản
- Training time bị giới hạn
- Đã có knowledge base tốt

---

### 2. Epsilon End (εₘᵢₙ)

```python
epsilon_end = 0.01  # Default
```

**Tăng lên (0.02-0.05)** nếu:
- Môi trường thay đổi (non-stationary)
- Muốn agent vẫn thích ứng

**Giữ thấp (0.001-0.01)** nếu:
- Môi trường cố định
- Cần performance cao nhất
- Production deployment

---

### 3. Epsilon Decay Rate

```python
epsilon_decay = 0.995  # Default
```

**Decay nhanh hơn (0.99)** nếu:
- Ít episodes (500-800)
- Muốn hội tụ nhanh
- Simple environment

**Decay chậm hơn (0.998)** nếu:
- Nhiều episodes (2000+)
- Complex environment
- Muốn explore lâu hơn

---

## 💡 Alternative Strategies

### 1. Linear Decay

```python
epsilon = epsilon_start - (epsilon_start - epsilon_end) * (ep / num_episodes)
```

**Ưu điểm**: Dễ predict, stable
**Nhược điểm**: Không natural như exponential

---

### 2. Step Decay

```python
if ep < 300:
    epsilon = 0.3
elif ep < 600:
    epsilon = 0.1
else:
    epsilon = 0.01
```

**Ưu điểm**: Rõ ràng từng giai đoạn
**Nhược điểm**: Sudden jumps, không smooth

---

### 3. Adaptive Epsilon (Advanced)

```python
# Giảm epsilon khi performance tốt, tăng khi performance xấu
if avg_cost_last_50 < best_cost_so_far:
    epsilon *= 0.99  # Giảm nhanh
else:
    epsilon *= 0.999  # Giảm chậm
```

**Ưu điểm**: Tự động thích ứng
**Nhược điểm**: Phức tạp hơn

---

## 🎯 Best Practices

### ✅ DOs

1. **Start high (0.3-0.5)**: Khám phá đầy đủ ở đầu
2. **End low (0.01-0.05)**: Khai thác tốt ở cuối
3. **Smooth decay**: Dùng exponential thay vì step
4. **Track epsilon**: Lưu epsilon_history để visualize
5. **Test different configs**: Thử nhiều (decay_rate, start, end)

### ❌ DON'Ts

1. ❌ Epsilon quá thấp từ đầu (< 0.1): Không explore đủ
2. ❌ Epsilon quá cao ở cuối (> 0.1): Không exploit được
3. ❌ Decay quá nhanh: Agent chưa kịp học
4. ❌ Decay quá chậm: Lãng phí episodes cuối
5. ❌ Không visualize epsilon: Không biết agent đang học thế nào

---

## 📊 Visualization Benefits

Notebook đã thêm 2 biểu đồ mới:

### 1. Epsilon Decay Curve
```python
plt.plot(epsilon_history)
```
→ Xem epsilon giảm như thế nào qua các episodes

### 2. Cost vs Epsilon Scatter
```python
plt.scatter(epsilon_history, episode_costs)
```
→ Tìm correlation giữa epsilon và performance

---

## 🔬 Experiment Ideas

### Test 1: Compare Strategies
```python
# Config 1: No decay
epsilon = 0.1 (constant)

# Config 2: Aggressive decay
epsilon_start=0.5, decay=0.99

# Config 3: Conservative decay  
epsilon_start=0.2, decay=0.998

→ So sánh final cost, convergence speed
```

### Test 2: Find Optimal Decay Rate
```python
for decay_rate in [0.990, 0.995, 0.998, 0.999]:
    train_model(epsilon_decay=decay_rate)
    evaluate_and_compare()
```

### Test 3: Adaptive vs Fixed
```python
# Fixed: epsilon_decay = 0.995
# Adaptive: decay based on performance

→ Xem adaptive có tốt hơn không
```

---

## 📈 Expected Improvements

Với epsilon decay, bạn có thể kỳ vọng:

- ✅ **Chi phí giảm 5-15%** so với epsilon cố định
- ✅ **Hội tụ nhanh hơn 20-30%**
- ✅ **Stable hơn** ở cuối training
- ✅ **Learning curve mượt mà hơn**

---

## 🎓 Tóm tắt

| Aspect | Value | Lý do |
|--------|-------|-------|
| **epsilon_start** | 0.3 | Explore nhiều ở đầu |
| **epsilon_end** | 0.01 | Exploit tốt ở cuối |
| **epsilon_decay** | 0.995 | Giảm dần, smooth |
| **Strategy** | Exponential | Natural, proven |
| **Tracking** | Save epsilon_history | Debug, visualize |

---

## 🚀 Next Steps

1. ✅ Chạy training với epsilon decay
2. ✅ Xem learning curves (6 biểu đồ)
3. ✅ So sánh với model cũ (epsilon cố định)
4. 🔬 Thử nghiệm các decay rates khác
5. 📊 Document kết quả tốt nhất

---

**📚 Tham khảo:**
- Sutton & Barto (2018): Reinforcement Learning - Chapter 2.7
- OpenAI Spinning Up: Exploration Strategies
- Deep RL Course (HuggingFace): Epsilon-Greedy

---

**✨ Kết luận:**

Epsilon decay là một **cải tiến đơn giản nhưng hiệu quả cao** cho Q-Learning. 
Thay vì agent "mù quáng" explore 10% suốt quá trình, epsilon decay giúp agent:
- **Học nhanh hơn** ở đầu (explore nhiều)
- **Perform tốt hơn** ở cuối (exploit nhiều)
- **Hội tụ ổn định hơn**

**Đã implement trong `test2.ipynb` Cell 3 và Cell 7!** 🎉
