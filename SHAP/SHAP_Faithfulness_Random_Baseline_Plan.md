# KẾ HOẠCH BỔ SUNG: RANDOM MASKING BASELINE CHO KIỂM ĐỊNH TÍNH TRUNG THỰC (SHAP FAITHFULNESS)

## 1. Lý do Khoa học & Mục tiêu Thực nghiệm (Rationale & Research Objectives)
* **Vấn đề phản biện:** Khi thực hiện can thiệp nhân quả bằng cách che $k$ đặc trưng ($k = 1 \dots 10$), nếu chỉ so sánh giữa MoRF và LeRF, một giả thuyết thách thức (confounding hypothesis) có thể đặt ra: *Mạng Neural Deep RL vốn rất nhạy cảm; việc che đi bất kỳ đặc trưng nào cũng khiến đầu ra sụt giảm chứ không riêng gì các đặc trưng do SHAP chỉ định.*
* **Giải pháp đối chứng:** Bổ sung chiến lược **Random Masking** đóng vai trò là một **Nhóm đối chứng (Control Group)** độc lập. Thực nghiệm này nhằm chứng minh một bất đẳng thức nghiêm ngặt về độ sụt giảm hiệu năng (Performance Drop):
  $$\text{Drop}_{\text{MoRF (Guided)}} > \text{Drop}_{\text{Random (Baseline)}} > \text{Drop}_{\text{LeRF (Guided)}}$$
* **Ý nghĩa:** Nếu bất đẳng thức trên được thỏa mãn, nhóm nghiên cứu có thể khẳng định một cách nghiêm ngặt rằng: Lời giải thích của SHAP mang tính nhân quả thực chất (causally informative), định vị đúng các điểm nút quyết định của Agent, thay vì chỉ là sự nhạy cảm thông tin ngẫu nhiên.

---

## 2. Thiết kế Phương pháp can thiệp Ngẫu nhiên (Perturbation Protocol)

Tại mỗi State $s$ thuộc tập 50 test states, song song với việc che theo thứ tự định sẵn của MoRF và LeRF, nhánh xử lý ngẫu nhiên sẽ hoạt động theo cơ chế sau:

* **Lấy mẫu chỉ mục ngẫu nhiên (Random Sampling):** Tại mỗi bước che $m$ đặc trưng ($m = 1, 2, \dots, 10$), hệ thống sẽ rút ngẫu nhiên không lặp một tập hợp các chỉ mục đặc trưng $S_{\text{rand}}$ từ toàn bộ không gian trạng thái $N = 660$ biến:
  $$S_{\text{rand}} \subset \{0, 1, 2, \dots, 659\}, \quad |S_{\text{rand}}| = m$$
* **Cơ chế khử nhiễu Monte Carlo (Bootstrapping Trials):** Do tính chất ngẫu nhiên có thể vô tình bốc trúng các biến cực kỳ quan trọng hoặc cực kỳ vô hại (gây ra sai số cục bộ), quy trình Random Masking tại mỗi trạng thái bắt buộc phải lặp lại $B = 30$ lần chạy độc lập. Giá trị sụt giảm cuối cùng ghi nhận tại trạng thái đó sẽ là giá trị kỳ vọng (trung bình cộng) qua 30 lần lặp nhằm đảm bảo tính ổn định toán học tuyệt đối.
* **Kỹ thuật che giá trị:** Các biến ngẫu nhiên nằm trong tập $S_{\text{rand}}$ sẽ bị ghi đè thông tin bằng giá trị trung vị hệ thống (`baseline_median`) đã được tính toán từ tập nền dữ liệu chuỗi cung ứng, loại bỏ thông tin biên mà không phá vỡ miền giá trị hợp lệ của mạng neural.

---

## 3. Công thức Toán học Đo lường Mở rộng (Extended Formulations)

Chúng tôi thiết lập công thức tính toán mức độ sụt giảm giá trị kỳ vọng cho nhóm đối chứng ngẫu nhiên sau khi đã qua bộ lọc Bootstrapping:

### 3.1. Đối với Tác nhân DQN (Value-based Agent)
Mức độ sụt giảm giá trị hành động tối ưu $Q(s, a^*)$ tương đối trung bình qua $B = 30$ lần lặp ngẫu nhiên:
$$\Delta Q_{\text{rand}}(m) = \frac{1}{B} \sum_{b=1}^{B} \frac{Q(s, a^*) - Q_{\text{rand\_masked}}^{(b)}(s, a^*)}{|Q(s, a^*)| + 1e^{-8}}$$

### 3.2. Đối với Tác nhân A2C_mod (Policy-based Agent)
Mức độ sụt giảm xác suất chọn chính sách tối ưu $\pi(a^*|s)$ tuyệt đối trung bình qua $B = 30$ lần lặp ngẫu nhiên:
$$\Delta \pi_{\text{rand}}(m) = \frac{1}{B} \sum_{b=1}^{B} \left[ \pi(a^*|s) - \pi_{\text{rand\_masked}}^{(b)}(a^*|s) \right]$$

---

## 4. Khung Biểu diễn Kết quả & Cấu trúc Minh chứng (Reporting Templates)

### 4.1. Cấu trúc Bảng số liệu Mới (Mở rộng Table 3 từ 2 dòng lên 3 dòng)
Hệ thống số liệu trong bài báo sẽ được cập nhật để tạo thế "kiềng ba chân" rõ ràng nhằm thuyết phục hoàn toàn phản biện:

**Bảng 3 (Cập nhật): Định lượng tính Trung thực của SHAP so với Nhánh đối chứng Ngẫu nhiên**

| Agent | Scenario | Chiến lược Can thiệp (Perturbation Strategy) | $\Delta Q$ / $\Delta \pi$ (Khi che Top-1) | $\Delta Q$ / $\Delta \pi$ (Khi che Top-5) | Tỷ lệ Đổi Hành động (ASR tại k=10) |
| :--- | :---: | :--- | :---: | :---: | :---: |
| **DQN** | **EASY** | Most Relevant First (MoRF) | *-xx.x%* | *-xx.x%* | *xx.x%* |
| | | **Random Masking (Baseline)** | **-x.x%** | **-xx.x%** | **xx.x%** |
| | | Least Relevant First (LeRF) | *-x.x%* | *-x.x%* | *x.x%* |
| **DQN** | **HARD** | Most Relevant First (MoRF) | *-xx.x%* | *-xx.x%* | *xx.x%* |
| | | **Random Masking (Baseline)** | **-x.x%** | **-xx.x%** | **xx.x%** |
| | | Least Relevant First (LeRF) | *-x.x%* | *-x.x%* | *x.x%* |
| **A2C_mod**| **EASY** | Most Relevant First (MoRF) | *-xx.x%* | *-xx.x%* | *xx.x%* |
| | | **Random Masking (Baseline)** | **-x.x%** | **-xx.x%** | **xx.x%** |
| | | Least Relevant First (LeRF) | *-x.x%* | *-x.x%* | *x.x%* |
| **A2C_mod**| **HARD** | Most Relevant First (MoRF) | *-xx.x%* | *-xx.x%* | *xx.x%* |
| | | **Random Masking (Baseline)** | **-x.x%** | **-xx.x%** | **xx.x%** |
| | | Least Relevant First (LeRF) | *-x.x%* | *-x.x%* | *x.x%* |

### 4.2. Thiết kế Đồ thị Đường (Perturbation Curve Chart Design)
Khi tái cấu trúc hàm vẽ đồ thị bằng thư viện `matplotlib` hoặc `seaborn`, mỗi biểu đồ con (Subplot) cho từng thực nghiệm sẽ được hiển thị với **3 đường biểu diễn**:
1. **Đường MoRF (Màu đỏ `#D62728`, Nét liền, Marker tròn `o`):** Đại diện cho việc che biến quan trọng theo định hướng của SHAP. Kỳ vọng đồ thị dốc xuống mạnh mẽ nhất (đối với $\Delta Q/\Delta \pi$) hoặc dốc lên nhanh nhất (đối với ASR).
2. **Đường Random Masking (Màu xám `#7F7F7F`, Nét đứt `--`, Marker tam giác `^`):** Đường đối chứng ngẫu nhiên. Đường này có xu hướng giảm/tăng tuyến tính một cách thoai thoải, đóng vai trò làm ranh giới nền ở giữa.
3. **Đường LeRF (Màu xanh dương `#1F77B4`, Nét liền, Marker vuông `s`):** Đại diện cho việc che biến vô hại. Đường đồ thị đi sát trục 0 (gần như nằm ngang), chứng minh thông tin bị mất không ảnh hưởng tới Agent.

---

## 5. Chiến lược Luận giải Học thuật chống Phản biện (Discussion Strategy)

Đoạn văn mẫu chuẩn tiếng Anh học thuật (Academic English) dưới đây được chuẩn bị sẵn để chèn trực tiếp vào phần **Discussion** nhằm hạ gục hoàn toàn lo ngại của Chuyên gia phản biện 1:

> *"To rigorously reject the counter-hypothesis that the performance degradation of the deep DRL agents is merely a trivial consequence of arbitrary information loss, we introduced a **Random Masking Baseline** constructed via 30 independent Monte Carlo bootstrapping trials per state. The empirical results illustrated in Table 3 and Figure X reveal a substantial, statistically significant fidelity gap between the explanation-guided strategy (MoRF) and the unguided random perturbations.*
>
> *Crucially, even in scenarios where the Action Switching Rate (ASR) initially experiences stagnation due to policy robustness (e.g., A2C_mod on EASY scenario), the internal decision confidence metrics ($\Delta Q$ and $\Delta \pi$) expose a stark contrast. Masking the top-1 critical feature identified by SHAP induces an immediate degradation of **[Insert MoRF %]**, which is **[Insert Factor]** times more severe than destroying a random feature baseline (**[Insert Random %]**). This empirical divergence conclusively proves that our proposed SHAP framework does not merely output human-plausible explanations, but precisely uncovers the intrinsic causal features driving the agent's supply chain policies."*