Câu hỏi 1. Phân tích SHAP cũng vẫn còn vấn đề. Môi trường gốc có 664 chiều trạng thái, nhưng SHAP chỉ được thực hiện trên ba đặc trưng tổng hợp: Inventory, Demand và Waste. Mặc dù việc tổng hợp có thể cải thiện khả năng đọc hiểu, nó cũng loại bỏ phần lớn cấu trúc ở cấp sản phẩm và cấp hệ thống — vốn là những yếu tố làm cho bài toán này khó và thú vị. Do đó, tuyên bố rằng SHAP kết nối “không gian đặc trưng trạng thái” với các quyết định DRL là bị phóng đại. Tốt nhất, bài báo chỉ đang giải thích quyết định ở mức tổng hợp rất thô. Các tác giả đã thừa nhận hạn chế này, nhưng bản thảo nên hoặc bổ sung thêm phân tích SHAP ở cấp sản phẩm hoặc phân tích top-k đặc trưng, hoặc thu hẹp đáng kể các tuyên bố về khả năng diễn giải ở cấp đặc trưng.      

Hướng chỉnh sửa: Ngoài phân tích SHAP gộp 3 nhóm, chúng tôi bổ sung top-k SHAP analysis trên các đặc trưng chi tiết hơn để xem những SKU hoặc biến hệ thống nào ảnh hưởng mạnh nhất đến quyết định của agent. 
- Vì sao vẫn giữ SHAP gộp 3 nhóm? 
- Thừa nhận hạn chế của aggregation (Đừng đưa ra hạn chế mạnh quá)
- Bổ sung top-k SHAP → thêm công thức tính độ quan trọng của từng feature
- Top-k SHAP nên chạy trên feature nào? → Tất cả 664 → Sau đó lấy top-10 hoặc top-20 feature có mean ∣SHAP∣cao nhất. 
- Lập bảng so sánh hai cấp SHAP analysis 

### Bảng 1: Phân cấp Hệ thống Giải thích SHAP (SHAP Interpretation Scope Matrix)

| SHAP Level | Input Features | Purpose | Interpretation Scope |
| :--- | :--- | :--- | :--- |
| **Aggregated SHAP** | Inventory, Demand, Waste | Provide compact managerial explanation | System-level operational drivers |
| **Top-k Feature SHAP** | SKU-level and system-level variables | Identify influential detailed features | Selected product-level and system-level decision drivers |

→ Bảng này giúp reviewer thấy bạn không còn đánh đồng 3 feature gộp với toàn bộ 664 chiều.  
Bảng top k feature (10 - 20 feature quan trọng thôi)
Biểu đồ Top-k SHAP feature importance 

Câu hỏi 2. Việc đánh giá chất lượng lời giải thích vẫn chưa đủ nghiêm ngặt. Các tác giả đã bổ sung các chỉ báo liên quan đến độ ổn định, độ thưa và tính nhất quán, nhưng bài báo vẫn chưa xác thực một cách thuyết phục liệu các lời giải thích có trung thành với cơ chế ra quyết định thực tế của tác nhân hay không. Ví dụ, MSX được mô tả như một “chứng chỉ” hoặc một biện minh tối thiểu đủ, nhưng phần xác thực thực nghiệm vẫn còn hạn chế. Bản thảo nên bổ sung các kiểm định mạnh hơn về tính trung thành, chẳng hạn như gây nhiễu hoặc che đi các thành phần phần thưởng/đặc trưng được xác định là quan trọng, rồi đo xem hành động được chọn, giá trị Q hoặc đầu ra chính sách có thay đổi như kỳ vọng hay không. Nếu không có điều này, phân tích giải thích có nguy cơ chỉ dừng lại ở mức mô tả thay vì được xác thực. 

Hướng chỉnh sửa: Kiểm chứng  bằng cách gây nhiễu hoặc che đi các thành phần phần thưởng/đặc trưng được xác định là quan trọng, rồi đo xem hành động được chọn, giá trị Q hoặc đầu ra chính sách có thay đổi như kỳ vọng hay không
Hướng triển khai
Các chỉ số đó chỉ cho thấy lời giải thích: có ổn định không, có ngắn gọn không, có nhất quán không. Nhưng reviewer muốn biết thêm: Nếu lời giải thích nói “feature/reward component này quan trọng”, thì khi mình che hoặc gây nhiễu nó, quyết định của agent có thay đổi không? 
Vd: MSX nói quyết định của agent phụ thuộc vào Service và Holding.
SHAP nói Demand_SKU_37 là feature quan trọng.
Vậy nếu che Service/Holding hoặc Demand_SKU_37, action/Q-value/policy probability có giảm hoặc thay đổi không?
Mục tiêu là trình bày rõ:
Che/gây nhiễu cái gì.
Che/gây nhiễu như thế nào.
Đo output nào.
So sánh với baseline nào.
Kết quả chứng minh được gì.

Nhóm 2: Kiểm định faithfulness cho SHAP
Mục tiêu
Kiểm tra xem các top-k SHAP features có thật sự ảnh hưởng đến output model không.
Ví dụ SHAP nói top-5 feature là:
demand_SKU_37
inventory_SKU_12
waste_SKU_88
warehouse_utilization
transport_capacity
Mình che các feature này rồi đo:
DQN: Q-value của action được chọn có giảm không.
A2C_mod: xác suất chọn action đó có giảm không.
Action có thay đổi không.


Câu hỏi 3. Bản thảo cũng cần mô tả kỹ thuật rõ ràng hơn về SHAP. Phản hồi cho phản biện trước vẫn chỉ nói rằng một “phương pháp quy kết đặc trưng dựa trên SHAP” được sử dụng, trong khi biến thể SHAP cụ thể và phân phối nền chưa được giải thích rõ ràng. Điều này rất quan trọng vì giá trị SHAP có thể thay đổi đáng kể tùy thuộc vào biến thể được dùng, chiến lược che/masking, các mẫu nền và cách xử lý các đặc trưng có tương quan. Các tác giả có đề cập đến đa cộng tuyến như một hướng nghiên cứu trong tương lai, nhưng điều này là chưa đủ, đặc biệt khi bài báo sử dụng SHAP như một trong ba trụ cột chính của khung đề xuất. 
Hướng chỉnh sửa: Reviewer 1 nói vẫn chưa nêu rõ SHAP variant, background distribution, masking strategy, và cách xử lý correlated features/multicollinearity.---> Bổ sung
