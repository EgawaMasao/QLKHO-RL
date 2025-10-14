# 🚨 Chẩn đoán: Agent học SAI - Chi phí cao hơn 1800 lần!

## 📊 Triệu chứng

```
✅ Q-table đã train:     81/82 giá trị khác 0
❌ Q-values CỰC ÂM:      -83,565 → 0
❌ Performance tệ hại:   55,081 €/ngày (vs 30 €/ngày)
❌ Tệ hơn baseline:      179,907%
```

---

## 🔍 Nguyên nhân chính: **REWARD SCALE QUÁ LỚN**

### Vấn đề

Trong code hiện tại:

```python
# Cell 7: Training
total_cost = holding_cost + backorder_cost + ordering_cost
reward = -total_cost  # ❌ Reward quá lớn (âm)

# Ví dụ:
# holding_cost = 0.0274 * 5 = 0.137 €
# backorder_cost = 20 * 5 = 100 €  
# ordering_cost = 50 €
# total_cost = 150.137 €
# reward = -150.137  # ❌ Q-values sẽ tích lũy thành số rất âm
```

### Tại sao Q-values âm cực lớn?

```
Episode 1, day 1:   Q[s,a] = 0 + 0.5 * (-150 + 0.7 * 0 - 0) = -75
Episode 1, day 2:   Q[s,a] = -75 + 0.5 * (-150 + 0.7 * (-75) - (-75)) = -113.75
...
Episode 1000:       Q[s,a] ≈ -83,565  # ❌ Tích lũy qua 1,000,000 steps
```

**Alpha = 0.5 quá cao** → cập nhật quá nhanh → Q-values phát tán

---

## ✅ Giải pháp 1: NORMALIZE REWARD (Khuyến nghị ⭐)

### Sửa Cell 7 - Training Loop

```python
# Thay vì:
reward = -total_cost

# Dùng:
reward = -total_cost / 100.0  # ✅ Normalize về [-1.5, 0]
```

**Lý do:**
- Cost thường 0-150 € → Reward -1.5 → 0
- Q-values sẽ ổn định hơn
- Alpha = 0.5 vẫn hoạt động tốt

---

## ✅ Giải pháp 2: GIẢM ALPHA (Dễ nhất)

### Sửa Cell 3 - Parameters

```python
# Thay vì:
alpha = 0.5  # ❌ Quá cao

# Dùng:
alpha = 0.1  # ✅ Ổn định hơn
```

**Lý do:**
- Alpha nhỏ → cập nhật chậm hơn → ổn định hơn
- Phù hợp với reward lớn
- Trade-off: học chậm hơn (cần nhiều episodes)

---

## ✅ Giải pháp 3: GIẢM GAMMA

### Sửa Cell 3 - Parameters

```python
# Thay vì:
gamma = 0.7  # Tính toán quá xa tương lai

# Dùng:
gamma = 0.5  # ✅ Tập trung vào reward gần
```

**Lý do:**
- Inventory management = short-term problem
- Gamma nhỏ → ít bị ảnh hưởng bởi tương lai xa
- Giảm variance của Q-values

---

## 🎯 Giải pháp KHUYẾN NGHỊ (Kết hợp)

### Step 1: Sửa Cell 3

```python
# Khởi tạo tham số cho mô hình
alpha = 0.2  # ✅ Giảm từ 0.5 → 0.2
gamma = 0.5  # ✅ Giảm từ 0.7 → 0.5
epsilon_start = 0.3
epsilon_end = 0.01
epsilon_decay = 0.995
```

### Step 2: Sửa Cell 7 - Normalize Reward

Tìm dòng:
```python
reward = -total_cost
```

Sửa thành:
```python
# Normalize reward về scale [-2, 0]
reward = -total_cost / 100.0  # ✅ Scale down 100 lần
```

### Step 3: Train lại

```
1. USE_PRETRAINED = False
2. Chạy Cell 1-9
3. Kiểm tra Q-values: nên từ -50 → 0
4. Đánh giá: nên tốt hơn baseline
```

---

## 📊 Expected Results sau khi sửa

```
Q-table min:           -50 → -10  ✅ Hợp lý
Q-table max:           0  ✅
Learned cost:          25-28 €/ngày  ✅
Traditional (r,q):     30 €/ngày
Improvement:           +5-15%  ✅
```

---

## 🔬 Giải thích chi tiết

### Tại sao alpha = 0.5 quá cao?

**Q-learning update formula:**
```
Q(s,a) ← Q(s,a) + α[r + γ·max Q(s',a') - Q(s,a)]
```

Nếu `α = 0.5`:
- Mỗi update thay đổi Q-value **50%**
- Với reward lớn (-150), mỗi step thay đổi ±75
- Sau 1000 episodes × 1000 days = 1,000,000 updates → phát tán

Nếu `α = 0.1`:
- Mỗi update chỉ thay đổi **10%**
- Ổn định hơn nhiều
- Cần nhiều episodes hơn để hội tụ

---

### Tại sao cần normalize reward?

**Không normalize:**
```
Day 1: cost = 150 € → reward = -150
Day 2: cost = 80 € → reward = -80
Q-values: [-150, -80, -120, ...]  # ❌ Quá lớn
```

**Có normalize (÷100):**
```
Day 1: cost = 150 € → reward = -1.5
Day 2: cost = 80 € → reward = -0.8
Q-values: [-1.5, -0.8, -1.2, ...]  # ✅ Hợp lý
```

---

## 🎓 Quy tắc chung cho Reward Design

### 1. Scale reward về [-1, 1]

```python
reward_min = -200  # Worst case cost
reward_max = 0     # Best case cost
reward = (reward - reward_min) / (reward_max - reward_min) * 2 - 1
```

### 2. Hoặc đơn giản: Chia cho constant

```python
reward = -cost / 100.0  # Đơn giản nhất
```

### 3. Điều chỉnh alpha phù hợp với reward scale

| Reward scale | Alpha khuyến nghị |
|--------------|-------------------|
| [-1, 1] | 0.3 - 0.5 |
| [-10, 10] | 0.1 - 0.3 |
| [-100, 100] | 0.05 - 0.1 |
| [-1000+] | ❌ Scale lại! |

---

## 🔧 Debugging Tips

### Check 1: Q-values range

```python
print(f"Q min: {Q.min():.2f}")  # Nên > -100
print(f"Q max: {Q.max():.2f}")  # Nên ≈ 0
print(f"Q mean: {Q.mean():.2f}") # Nên -50 → 0
```

### Check 2: Reward range per episode

```python
print(f"Avg reward per day: {np.mean([...rewards...])}")
# Nên -2 → 0 (nếu normalize)
```

### Check 3: Q-values convergence

```python
# Vẽ Q-values evolution
plt.plot([Q.mean() for Q in Q_history])
# Nên hội tụ (flatten) sau 500-800 episodes
```

---

## 📚 Tham khảo

1. **Sutton & Barto (2018)** - Chapter 6.5: Q-learning
2. **Reward Shaping** - Ng et al. (1999)
3. **DeepMind** - DQN paper về reward clipping

---

## ✅ Action Items

- [ ] 1. Sửa `alpha = 0.2` trong Cell 3
- [ ] 2. Sửa `gamma = 0.5` trong Cell 3
- [ ] 3. Thêm `reward = -total_cost / 100.0` trong Cell 7
- [ ] 4. Train lại từ Cell 7
- [ ] 5. Kiểm tra Q-values trong Cell 16
- [ ] 6. Đánh giá lại performance
- [ ] 7. Expected: Improvement 5-15%

---

## 🎯 Kết luận

**Root cause:** Reward scale quá lớn + Alpha quá cao

**Solution:** 
1. Normalize reward (÷100)
2. Giảm alpha (0.5 → 0.2)
3. Giảm gamma (0.7 → 0.5)

**Expected outcome:** Agent học đúng, improve 5-15% vs baseline

---

**Tác giả:** GitHub Copilot
**Ngày:** 2025-10-15
