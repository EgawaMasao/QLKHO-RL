# 🎯 Ngữ Cảnh Mong Muốn để Huấn Luyện Agent Q-Learning

## 📋 Tổng quan bài toán

### Vấn đề kinh doanh
Một nhà bán lẻ cần quản lý tồn kho sản phẩm để:
- ✅ **Đáp ứng nhu cầu khách hàng** (tránh hết hàng)
- ✅ **Giảm thiểu chi phí** (lưu trữ + đặt hàng + thiếu hàng)
- ✅ **Ra quyết định tự động** mỗi ngày: Có nên đặt hàng không?

### Mục tiêu học máy
Train một **agent thông minh** sử dụng **Q-Learning** để:
- Học từ kinh nghiệm (trial & error)
- Tự động quyết định **khi nào đặt hàng** và **đặt bao nhiêu**
- Tối ưu hóa chi phí dài hạn (long-term cost minimization)

---

## 🏭 Môi trường kinh doanh (Environment)

### 1. Thông số sản phẩm
```python
mu = 3.0           # Nhu cầu trung bình: 3 sản phẩm/ngày
sigma = 1.0        # Độ biến động nhu cầu: ±1 sản phẩm
LT = 1             # Lead time: Hàng đến sau 1 ngày kể từ khi đặt
```

**Ý nghĩa thực tế:**
- Khách hàng mua trung bình 3 sản phẩm/ngày
- Nhu cầu dao động: Có ngày 1-2 sản phẩm, có ngày 4-5 sản phẩm
- Nhà cung cấp giao hàng sau 1 ngày → Phải dự đoán trước!

### 2. Cấu trúc chi phí
```python
O = 50.0 €         # Chi phí đặt hàng (ordering cost)
                   # - Phí vận chuyển
                   # - Chi phí xử lý đơn hàng
                   # - Chi phí hành chính

h = 10/365 €/ngày  # Chi phí lưu trữ (holding cost)
                   # - Tiền thuê kho
                   # - Bảo hiểm
                   # - Hao hụt, mất mát

b = 20.0 €         # Chi phí thiếu hàng (backorder cost)
                   # - Mất lòng tin khách hàng
                   # - Phải giao hàng khẩn cấp
                   # - Mất doanh thu

q = 6              # Số lượng đặt mỗi lần (order quantity)
```

**Trade-offs kinh doanh:**
- **Đặt hàng thường xuyên:** Chi phí ordering cao (O = 50€)
- **Tồn kho nhiều:** Chi phí lưu trữ cao (h × inventory)
- **Tồn kho ít:** Nguy cơ hết hàng → chi phí thiếu hàng (b × shortage)

### 3. Biến trạng thái (State)
```python
State = Inventory Position (IP)
IP = On-hand inventory + Orders in transit - Backorders
Range: [-20, 20] → 41 states
```

**Ý nghĩa các trạng thái:**
- **IP < 0:** Thiếu hàng (backorders) - Khách đã đặt nhưng chưa có hàng
- **IP = 0:** Vừa đủ (sắp hết)
- **IP = 3-6:** Tồn kho an toàn (safety stock)
- **IP > 10:** Tồn kho dư thừa (overstock)

### 4. Không gian hành động (Action)
```python
Action 0: Không đặt hàng (Do nothing)
Action 1: Đặt hàng q=6 sản phẩm
```

**Quyết định hàng ngày:**
- Mỗi sáng, agent xem IP hiện tại
- Chọn: Đặt hàng 6 sản phẩm HOẶC chờ thêm?

---

## 🎓 Quy trình học (Learning Process)

### 1. Exploration vs Exploitation
```python
epsilon_start = 0.3    # 30% explore ở đầu
epsilon_end = 0.01     # 1% explore ở cuối
epsilon_decay = 0.998  # Giảm dần qua episodes
```

**Giai đoạn học:**

#### Phase 1: Early Learning (Episodes 1-500, ε ≈ 0.3 → 0.15)
- **Behavior:** Agent thử nhiều hành động khác nhau
- **Goal:** Khám phá tất cả states và consequences
- **Example:** Thử đặt hàng khi IP=10 (tồn cao) → Phát hiện chi phí cao

#### Phase 2: Intermediate (Episodes 500-1500, ε ≈ 0.15 → 0.03)
- **Behavior:** Agent bắt đầu khai thác kiến thức đã học
- **Goal:** Fine-tune policy, kiểm tra các states ít gặp
- **Example:** Học được nên đặt hàng khi IP≤3

#### Phase 3: Exploitation (Episodes 1500-2000, ε ≈ 0.03 → 0.01)
- **Behavior:** Chủ yếu follow learned policy (99%)
- **Goal:** Consolidate knowledge, final refinements
- **Example:** Policy ổn định, chỉ explore 1% để avoid local optima

### 2. Reward Signal (Feedback)
```python
reward = -total_cost / REWARD_SCALE

total_cost = ordering_cost + holding_cost + backorder_cost
           = O·I[order] + h·max(inventory,0) + b·max(-inventory,0)
```

**Cách agent học từ reward:**
- **Reward cao (gần 0):** Chi phí thấp → Hành động tốt
- **Reward thấp (rất âm):** Chi phí cao → Hành động xấu

**Ví dụ:**
```
Scenario A: IP=2 → Đặt hàng → Cost=50+1=51€ → Reward=-0.51
Scenario B: IP=2 → Không đặt → Hết hàng → Cost=0+60=60€ → Reward=-0.60
→ Agent học: Đặt hàng tốt hơn khi IP thấp!
```

### 3. Q-Learning Update Rule
```python
Q(s,a) ← Q(s,a) + α[r + γ·max Q(s',a') - Q(s,a)]
```

**Các tham số:**
- **α = 0.2** (learning rate): Học chậm, ổn định
- **γ = 0.95** (discount factor): Quan tâm 95% future rewards
- **Episode length = 300 days**: Đủ dài để thấy consequences

**Cách update hoạt động:**
1. Agent ở state s (e.g., IP=3), chọn action a (e.g., đặt hàng)
2. Nhận reward r = -0.51 (chi phí 51€)
3. Chuyển sang state s' (e.g., IP=6 sau khi hàng về)
4. Update Q(IP=3, đặt hàng) dựa trên:
   - Reward ngay lập tức: -0.51
   - Future value: γ × max Q(IP=6, ...)
   - Mix với old Q-value: α = 20% new, 80% old

### 4. Training Episodes
```python
num_episodes = 2000
episode_length = 300 days
```

**Mỗi episode mô phỏng:**
1. **Day 1-300:** Agent điều hành kho hàng
2. **Mỗi ngày:**
   - Xem IP hiện tại
   - Quyết định đặt hàng hay không (ε-greedy)
   - Nhu cầu random xuất hiện
   - Nhận hàng (nếu đã đặt 1 ngày trước)
   - Tính chi phí
   - Update Q-table
3. **End of episode:** Reset môi trường, bắt đầu lại

**Tổng training:**
- **2000 episodes × 300 days = 600,000 steps**
- Mỗi state (41 states) được visit trung bình ~14,600 lần
- Đủ để học cả states hiếm (IP=-20, IP=20)

---

## 🎯 Ngữ cảnh mong muốn Agent học được

### 1. Basic Inventory Logic
**Mong muốn:**
- ✅ IP thấp → Đặt hàng (tránh hết hàng)
- ✅ IP cao → Không đặt hàng (tránh tồn dư)
- ✅ Cân bằng ordering frequency vs inventory level

**Policy lý tưởng (tương tự r,q policy):**
```
Nếu IP ≤ r (reorder point) → Đặt hàng q sản phẩm
Ngược lại → Không đặt hàng

Với r ≈ 2-4 (phụ thuộc vào mu, LT, safety stock)
```

### 2. Lead Time Awareness
**Mong muốn:**
Agent hiểu rằng:
- Hàng đến sau **1 ngày** → Phải dự đoán trước
- Nếu IP=4 hôm nay, ngày mai demand=3 → IP=1
- Phải đặt hàng **HÔM NAY** để hàng về **NGÀY MAI**

**Behavior mong muốn:**
```
State: IP=3, demand dự kiến 3/ngày
→ Ngày mai IP ≈ 0 (nguy hiểm!)
→ Action: Đặt hàng ngay để hàng về ngày mai (IP=6)
```

### 3. Cost Trade-off Understanding
**Mong muốn:**
Agent tự học được balance:

#### Trade-off 1: Ordering cost vs Frequency
```
Strategy A: Đặt hàng thường xuyên (IP threshold cao)
  - Pros: Ít thiếu hàng
  - Cons: Nhiều lần đặt → Ordering cost cao

Strategy B: Đặt hàng hiếm (IP threshold thấp)
  - Pros: Ít ordering cost
  - Cons: Nguy cơ thiếu hàng → Backorder cost cao
```

#### Trade-off 2: Holding cost vs Backorder cost
```
h = 10/365 ≈ 0.027 €/day/unit (thấp)
b = 20 € (cao gấp 730 lần!)

→ Agent nên học: Thiếu hàng TỆ HƠN NHIỀU so với tồn dư
→ Prefer slightly higher inventory than stockout
```

### 4. Stochastic Demand Handling
**Mong muốn:**
Agent học được xử lý uncertainty:

```python
Demand ~ N(μ=3, σ=1)
→ 68% ngày: demand ∈ [2, 4]
→ 95% ngày: demand ∈ [1, 5]
→ Hiếm khi: demand = 0 hoặc 6+
```

**Safety stock logic mong muốn:**
```
Reorder point r không nên = μ × LT = 3 × 1 = 3
Vì 50% trường hợp demand > 3 → Hết hàng!

Nên: r = μ × LT + z × σ × √LT
     = 3 × 1 + 1.65 × 1 × 1
     = 4.65 ≈ 5 (cho 95% service level)
```

### 5. Long-term Planning
**Mong muốn:**
Với γ=0.95, agent nên quan tâm ~20 bước tương lai:

```
γ^1 = 0.95    → Ngày mai quan trọng 95%
γ^2 = 0.90    → 2 ngày sau quan trọng 90%
γ^5 = 0.77    → 5 ngày sau quan trọng 77%
γ^10 = 0.60   → 10 ngày sau quan trọng 60%
γ^20 = 0.36   → 20 ngày sau quan trọng 36%
```

**Behavior mong muốn:**
- Không chỉ optimize hôm nay
- Hiểu rằng quyết định hôm nay ảnh hưởng 2-3 tuần sau
- Ví dụ: Đặt hàng hôm nay → Inventory cao 5 ngày sau → Holding cost kéo dài

---

## 🚀 Kịch bản Training Lý tưởng

### Episode 1-100: Chaotic Exploration
**Hành vi:**
- Agent thử random: Đặt hàng khi IP=15, không đặt khi IP=-10, v.v.
- Chi phí cao: 100,000-300,000 € per episode
- Q-values chưa ổn định, update liên tục

**Học được:**
- States nào được visit thường xuyên (IP ∈ [-5, 10])
- States nào hiếm (IP < -10 hoặc IP > 15)
- Backorder cost RẤT ĐẮT (b=20€)

### Episode 100-500: Pattern Recognition
**Hành vi:**
- Bắt đầu thấy pattern: IP thấp → Nên đặt hàng
- Chi phí giảm: 50,000-100,000 € per episode
- Epsilon giảm: 0.30 → 0.15

**Học được:**
- Reorder point nên ở đâu (~IP=3-5)
- Không nên đặt hàng khi IP>8
- Lead time = 1 ngày → Cần anticipate

### Episode 500-1500: Policy Refinement
**Hành vi:**
- Policy gần ổn định: Đặt hàng khi IP≤4
- Chi phí ổn định: 20,000-40,000 € per episode
- Epsilon giảm: 0.15 → 0.03

**Học được:**
- Fine-tune reorder point: IP=3 hay IP=4?
- Handle edge cases: IP=-15, IP=18
- Balance holding vs backorder

### Episode 1500-2000: Convergence
**Hành vi:**
- Policy hội tụ, ít thay đổi
- Chi phí thấp nhất: ~20,000 € per episode
- Epsilon minimal: 0.03 → 0.01

**Học được:**
- Stable policy: IP≤3 → Order, IP≥4 → Don't order
- Q-values hội tụ
- Ready for deployment!

---

## 📊 Chỉ số đánh giá thành công

### 1. Q-table Health
```python
✅ Mong muốn:
- Tất cả 82 Q-values (41×2) đều ≠ 0 (tất cả states visited)
- Q-values phân bố hợp lý: min ≈ -20,000, max ≈ -500
- Q(low IP, order) > Q(low IP, no order)
- Q(high IP, no order) > Q(high IP, order)
```

### 2. Learning Curve
```python
✅ Mong muốn:
- Episode costs giảm dần: 300,000 → 20,000 €
- Convergence rõ ràng sau episode 1500
- Variance giảm (policy ổn định)
```

### 3. Policy Quality
```python
✅ Mong muốn:
- Learned cost ≈ (r,q) cost ± 20%
- Policy logic hợp lý: Threshold rõ ràng
- Robust với random seeds khác nhau
```

### 4. Operational Metrics
```python
✅ Mong muốn:
- Service level: >95% (ít thiếu hàng)
- Average inventory: 3-6 units (hợp lý)
- Order frequency: ~30-50% days (không quá thường xuyên)
```

---

## 🎬 Kết luận: Ngữ cảnh mong muốn tóm gọn

**Agent lý tưởng sau khi training:**

1. **Hiểu business logic:** 
   - Low inventory → Order to avoid stockout
   - High inventory → Don't order to save costs

2. **Handle uncertainty:**
   - Demand stochastic → Maintain safety stock
   - Lead time → Plan 1 day ahead

3. **Optimize long-term:**
   - Not just today's cost, but future 20 days
   - Balance ordering frequency vs inventory level

4. **Converged policy:**
   - Clear reorder point (r ≈ 3-5)
   - Consistent behavior across episodes
   - Cost ≈ 30-60 €/day (comparable to optimal)

5. **Robust và stable:**
   - Works với different random seeds
   - Q-values hội tụ, không oscillate
   - Ready for real-world deployment

---

## 📚 So sánh với (r,q) Policy

| Aspect | (r,q) Policy | Q-Learning Agent (Mong muốn) |
|--------|-------------|-------------------------------|
| **Logic** | If IP≤r → Order | Learn optimal threshold từ data |
| **Parameters** | r, q chosen manually | Learned automatically |
| **Flexibility** | Fixed rule | Adapt to different costs/demands |
| **Optimality** | Good if r,q tuned well | Potentially better (learn non-linear) |
| **Training** | No training needed | 2000 episodes ≈ 30 minutes |
| **Interpretability** | Very clear | Q-table harder to interpret |

**Kỳ vọng cuối cùng:**
- Q-Learning **match hoặc beat** (r,q) by 0-30%
- Nếu tệ hơn >50% → Có vấn đề (như đã fix)
- Nếu tốt hơn >30% → Excellent! Q-learning found better pattern

---

**🎯 TÓM LẠI:** Agent cần học trong môi trường stochastic inventory với demand dao động, trade-offs giữa 3 loại chi phí, và lead time 1 ngày. Sau 2000 episodes với epsilon decay và gamma=0.95, agent nên hội tụ về policy tương tự (r,q) với reorder point ~3-5, cost ~30-60€/day, và hành vi stable & logical! 🚀
