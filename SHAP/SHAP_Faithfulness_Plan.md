# KẾ HOẠCH KIỂM ĐỊNH TÍNH TRUNG THỰC CHO SHAP (SHAP FAITHFULNESS VERIFICATION PLAN)

## 1. Bản chất của Vấn đề & Mục tiêu Thí nghiệm
* **Phản biện của Chuyên gia:** Các chỉ số hiện tại (Stability, FCS, CAS) mới chỉ chứng minh lời giải thích *ổn định* và *nhất quán*, nhưng chưa chứng minh được tính *trung thực* (Faithfulness/Fidelity). Có rủi ro bộ giải thích đưa ra kết quả trông hợp lý với con người (Plausible) nhưng lại sai lệch so với cơ chế kích hoạt mạng thần kinh thực tế của Agent.
* **Mục tiêu:** Thực hiện các thực nghiệm **Can thiệp nhân quả (Causal Interventions)** bằng cách che/gây nhiễu (Masking/Perturbation) các đặc trưng được SHAP định nghĩa là quan trọng, sau đó đo đạc sự thay đổi logic đầu ra của Agent để chứng minh mối quan hệ nhân quả nghiêm ngặt.

---

## 2. Phương pháp Thực nghiệm (Perturbation Protocols)

Chúng ta áp dụng hai chiến lược can thiệp đối nghịch chuẩn quốc tế trong XAI:
1. **MoRF (Most Relevant First):** Che dần các đặc trưng từ quan trọng nhất xuống (Top-1, Top-2, ..., Top-k).
   * *Kỳ vọng toán học:* Đầu ra của mô hình ($Q$-value hoặc xác suất Policy) phải **sụt giảm cực kỳ nhanh và ngặt nghèo** (độ dốc lớn).
2. **LeRF (Least Relevant First):** Che dần các đặc trưng từ ít quan trọng nhất ngược lên (Xếp hạng 660, 659, ...).
   * *Kỳ vọng toán học:* Đầu ra của mô hình **gần như không biến động** (đường đồ thị đi ngang), chứng minh Agent thực sự bỏ qua các đặc trưng này đúng như SHAP dự đoán.

### Kỹ thuật Che thông tin (Masking Mechanism)
Trong bài toán Chuỗi cung ứng, không thể gán biến trạng thái bằng `0` một cách tùy tiện (vì giá trị `0` mang ý nghĩa nghiệp vụ: hết hàng, không có nhu cầu). 
* **Giải pháp:** Sử dụng **Baseline Substitution**. Thay thế giá trị của đặc trưng bị che bằng giá trị trung vị (Median) hoặc giá trị từ tập dữ liệu nền (`background_660`) để triệt tiêu thông tin biên mà không làm hỏng cấu trúc đầu vào của mạng.

---

## 3. Các Chỉ số Đo lường & Baseline (Metrics & Targets)

Với mỗi State $s$ trong tập 50 test states, ta xác định hành động tối ưu ban đầu là $a^* = \arg\max Q(s, a)$ (đối với DQN) hoặc $a^* = \arg\max \pi(a|s)$ (đối với A2C_mod). Ta tiến hành che $m$ đặc trưng và đo đạc:

1. **Đối với DQN (Value-based Agent):** Mức độ sụt giảm giá trị $Q$ tương đối:
$$\Delta Q(m) = \frac{Q(s, a^*) - Q_{masked}(s, a^*)}{Q(s, a^*)}$$
2. **Đối với A2C_mod (Policy-based Agent):** Mức độ sụt giảm xác suất chọn hành động tối ưu:
$$\Delta \pi(m) = \pi(a^*|s) - \pi_{masked}(a^*|s)$$
3. **Chỉ số chung - Tỷ lệ Đổi Hành động (Action Switching Rate - ASR):** Tỷ lệ phần trăm các trạng thái mà Agent thay đổi quyết định sang hành động khác sau khi bị che thông tin.

---

## 4. Khung Biểu diễn Kết quả Thực nghiệm

Hệ thống bảng số liệu mới này sẽ được đưa vào bài báo tại mục **"Sec 4.X. Faithfulness Verification via Feature Perturbation"**.

### Bảng 3: Định lượng tính Trung thực (Faithfulness) của SHAP qua phân đoạn MoRF/LeRF

| Agent | Scenario | Chiến lược Can thiệp (Perturbation Strategy) | $\Delta Q$ hoặc $\Delta \pi$ (Khi che Top-1) | $\Delta Q$ hoặc $\Delta \pi$ (Khi che Top-5) | Tỷ lệ Đổi Hành động (ASR) |
| :--- | :---: | :--- | :---: | :---: | :---: |
| **DQN** | **EASY** | Most Relevant First (MoRF) | *-xx.x%* | *-xx.x%* | *xx.x% (Cao)* |
| | | Least Relevant First (LeRF) | *-x.x%* | *-x.x%* | *x.x% (Thấp)* |
| **DQN** | **HARD** | Most Relevant First (MoRF) | *-xx.x%* | *-xx.x%* | *xx.x%* |
| | | Least Relevant First (LeRF) | *-x.x%* | *-x.x%* | *x.x%* |
| **A2C_mod**| **EASY** | Most Relevant First (MoRF) | *-xx.x%* | *-xx.x%* | *xx.x%* |
| | | Least Relevant First (LeRF) | *-x.x%* | *-x.x%* | *x.x%* |
| **A2C_mod**| **HARD** | Most Relevant First (MoRF) | *-xx.x%* | *-xx.x%* | *xx.x%* |
| | | Least Relevant First (LeRF) | *-x.x%* | *-x.x%* | *x.x%* |

### Trực quan hóa đồ thị (Perturbation Curve Chart)
* **Mô tả đồ thị:** Vẽ đồ thị dạng đường (Line chart). Trục $X$ thể hiện *Số lượng đặc trưng bị che tăng dần (từ 0 đến 10)*. Trục $Y$ thể hiện *Mức độ sụt giảm hiệu năng hoặc niềm tin của mô hình ($\Delta Q$ hoặc $\Delta \pi$)*.
* **Kỳ vọng trực quan:** Đường **MoRF (màu đỏ)** dốc xuống cực kỳ nhanh. Đường **LeRF (màu xanh)** duy trì vị trí tiệm cận đường 0 (đi ngang).

---

## 5. Chiến lược Biện luận Học thuật (Response & Discussion Strategy)

Khi viết phần thảo luận kết quả để thuyết phục Reviewer, chúng ta sẽ tập trung vào hai luận điểm chính:

1. **Xác thực mối quan hệ nhân quả (Causal Validation):**
   Khẳng định kết quả thực nghiệm chứng minh SHAP không chỉ tạo ra các biểu đồ giải thích "đẹp mắt" mà thực sự tìm đúng các điểm nút mạng thần kinh. Ví dụ: *"Khi chỉ can thiệp vào duy nhất đặc trưng xếp hạng 1 bởi SHAP, giá trị Q-value sụt giảm ngay lập tức [X]%, vượt trội hoàn toàn so với việc che đồng thời 10 đặc trưng cuối bảng (chỉ gây biến động < 1.5%). Điều này chứng minh tính trung thực cao (High Fidelity) của bộ giải thích."*
2. **So sánh tính nhạy cảm kiến trúc (Architectural Robustness):**
   Phân tích sự khác biệt giữa mạng Q-value (DQN) và mạng Stochastic Policy ($\text{A2C\_mod}$). Thông thường, đường MoRF của $\text{A2C\_mod}$ sẽ có độ dốc thoai thoải hơn DQN một chút. Chúng ta sẽ tận dụng điểm này làm đóng góp (Contribution): *"Kiến trúc Actor-Critic ($\text{A2C\_mod}$) thể hiện tính chống nhiễu (Robustness) tốt hơn trước các nhiễu động thông tin cấp SKU, do mạng chính sách học được phân phối xác suất ngẫu nhiên để bù đắp thông tin thiếu hụt, thay vì ước lượng giá trị tuyệt đối như mạng Q của DQN."*