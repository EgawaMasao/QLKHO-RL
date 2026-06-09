# KẾ HOẠCH BỔ SUNG PHÂN TÍCH SHAP ĐA CẤP ĐỘ (MULTI-LEVEL SHAP EXPANSION PLAN)

## 1. Đặt vấn đề & Mục tiêu chỉnh sửa
* **Phản biện của Chuyên gia:** Việc gộp 664 chiều trạng thái thành 3 đặc trưng vĩ mô (*Inventory, Demand, Waste*) làm mất mát cấu trúc cấp sản phẩm (SKU) và cấp hệ thống, dẫn đến việc tuyên bố giải thích toàn bộ quyết định của Agent bị phóng đại.
* **Mục tiêu:** 
    * Thu hẹp tuyên bố một cách khoa học (giảm bớt việc phóng đại).
    * Bổ sung phân tích **Top-k Micro-level SHAP** trên toàn bộ 664 không gian biến gốc để chứng minh tính minh bạch cấp vận hành (Operational-level Transparency).
    * Giữ lại cấu trúc **Macro-level SHAP** (3 nhóm gộp) như một khung định hướng chiến lược cho nhà quản trị.

---

## 2. Khung Lý thuyết & Quản lý Kỳ vọng (Formatting Matrix)

Để reviewer thấy rõ sự khác biệt và vai trò của từng cấp độ, hệ thống giải thích mới sẽ được định nghĩa theo bảng cấu trúc sau:

### Bảng 1: Phân cấp Hệ thống Giải thích SHAP (SHAP Interpretation Scope Matrix)

| SHAP Level | Input Features | Purpose | Interpretation Scope |
| :--- | :--- | :--- | :--- |
| **Aggregated SHAP** | Inventory, Demand, Waste | Provide compact managerial explanation | System-level operational drivers |
| **Top-k Feature SHAP** | SKU-level and system-level variables | Identify influential detailed features | Selected product-level and system-level decision drivers |

> **Văn phong hàn lâm khuyến nghị khi biện luận:** 
> *"Việc gộp 3 nhóm đặc trưng vĩ mô (Macro-features) đóng vai trò như một Khung định hướng chiến lược (Strategic Cognitive Framework) giúp người vận hành nhận diện nhanh xu hướng hành vi tổng thể của Agent. Nhằm loại bỏ hoàn toàn rủi ro thiên kiến do việc gộp dữ liệu (Aggregation Bias) và đào sâu vào cấu trúc vi mô của bài toán, chúng tôi mở rộng phân tích xuống cấp độ đặc trưng thô gốc (Raw Feature Space) thông qua bộ lọc Top-k."*

---

## 3. Quy trình Triển khai Thực nghiệm (Action Plan)

### Bước 1: Trích xuất dữ liệu Thống kê Top-k
1. Chạy mô hình giải thích SHAP trên tập dữ liệu kiểm thử (Test set) gồm $N$ episodes đại diện để đảm bảo phân phối hội tụ.
2. Áp dụng công thức tính toán độ quan trọng vi mô (Mean Absolute SHAP) cho từng thuộc tính $f_j$ trong toàn bộ 664 chiều trạng thái:
$$I_{Micro}(f_j) = \frac{1}{N}\sum_{n=1}^{N} \vert \phi_j^{(n)} \vert$$
3. Sắp xếp giảm dần và trích xuất ra **Top-10** hoặc **Top-20** đặc trưng có giá trị cao nhất.

### Bước 2: Thiết lập Bảng kết quả Thực nghiệm
Điền các giá trị thực nghiệm sau khi chạy vào bảng cấu trúc chuẩn dưới đây:

### Bảng 2: Top-k Đặc trưng gốc có mức độ ảnh hưởng lớn nhất đến Quyết định của Agent
| Xếp hạng (Rank) | Tên Đặc trưng Gốc (Raw Feature Name) | Thuộc nhóm vĩ mô (Macro Group) | Mean $\vert SHAP \vert$ | Ý nghĩa Nghiệp vụ Chuỗi cung ứng (Domain Insight) |
| :---: | :--- | :---: | :---: | :--- |
| **1** | `Demand_SKU_[X]` | Demand | *0.xxxx* | Agent ưu tiên phản ứng cực đoan với mã hàng cốt lõi để bảo vệ Service Level. |
| **2** | `Inventory_SKU_[X]` | Inventory | *0.xxxx* | Đối ứng trực tiếp với Rank 1 nhằm tính toán Điểm tái đặt hàng (Reorder Point). |
| **3** | `Waste_SKU_[Y]` | Waste | *0.xxxx* | Điểm kích hoạt nhạy cảm: Agent chủ động xả hàng/giảm đặt khi tiệm cận hạn dùng. |
| **...** | ... | ... | *0.xxxx* | ... |
| **10** | `Inventory_SKU_[Z]` | Inventory | *0.xxxx* | Biến động tồn kho của mã hàng nhóm Long-tail có chi phí lưu kho cao. |

### Bước 3: Trực quan hóa (Biểu đồ Top-k SHAP Importance)
* **Dạng đồ thị:** Biểu đồ thanh ngang (**Horizontal Bar Chart**), sắp xếp trục dọc từ trên xuống dưới theo thứ tự giảm dần của độ quan trọng.
* **Mã hóa màu sắc (Color Coding):** Không dùng một màu đơn điệu. Hãy đổ màu các thanh thanh dựa theo nhóm thuộc tính gốc của nó:
    * 🟦 Màu Xanh dương: Dành cho các đặc trưng chi tiết thuộc nhóm **Demand**.
    * 🟩 Màu Xanh lá: Dành cho các đặc trưng chi tiết thuộc nhóm **Inventory**.
    * 🟥 Màu Đỏ: Dành cho các đặc trưng chi tiết thuộc nhóm **Waste**.
* **Mục tiêu đồ thị:** Giúp Reviewer thấy ngay sự liên kết trực quan: Vừa biết được chính xác SKU cụ thể nào đang dẫn dắt quyết định (Vi mô), vừa thấy được màu sắc nào đang chiếm lĩnh đồ thị (Vĩ mô).

---

## 4. Các Luận điểm Biện luận Cốt lõi (Argumentation Insights)

Khi viết phần thảo luận kết quả mới, cần tập trung làm nổi bật 2 hiện tượng nghiệp vụ sâu sắc mà mô hình học máy đã tự phát hiện:

1. **Sự phân hóa biên độ nhạy cảm (Marginal Sensitivity):** 
   Chứng minh rằng Agent hình thành cơ chế "nhận diện ưu tiên". Đối với các SKU "Hot-selling", trị tuyệt đối SHAP của biến `Demand` sẽ vượt trội, thể hiện việc Agent sẵn sàng chấp nhận rủi ro lãng phí (Waste) ở mức nhẹ để đảm bảo không đứt gãy chuỗi cung ứng.
2. **Sự tương tác phi tuyến tính cấp sản phẩm (Local Non-linearity):**
   Chỉ ra các điểm gãy (ngưỡng nhạy cảm). Ví dụ: Biến `Waste` của các SKU có hạn sử dụng ngắn (Short shelf-life) sẽ có trọng số SHAP vọt lên rất cao ngay khi lượng tồn kho vượt ngưỡng an toàn $\rightarrow$ Chứng minh Agent thực sự hiểu sâu sắc cấu trúc độc lập của từng sản phẩm chứ không chỉ học máy móc trên dữ liệu cào bằng.