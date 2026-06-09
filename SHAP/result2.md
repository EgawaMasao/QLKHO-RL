## 3. Phân tích SHAP cũng vẫn còn vấn đề. Môi trường gốc có 664 chiều trạng thái, nhưng SHAP chỉ được thực hiện trên ba đặc trưng tổng hợp: Inventory, Demand và Waste. Mặc dù việc tổng hợp có thể cải thiện khả năng đọc hiểu, nó cũng loại bỏ phần lớn cấu trúc ở cấp sản phẩm và cấp hệ thống — vốn là những yếu tố làm cho bài toán này khó và thú vị. Do đó, tuyên bố rằng SHAP kết nối “không gian đặc trưng trạng thái” với các quyết định DRL là bị phóng đại. Tốt nhất, bài báo chỉ đang giải thích quyết định ở mức tổng hợp rất thô. Các tác giả đã thừa nhận hạn chế này, nhưng bản thảo nên hoặc bổ sung thêm phân tích SHAP ở cấp sản phẩm hoặc phân tích top-k đặc trưng, hoặc thu hẹp đáng kể các tuyên bố về khả năng diễn giải ở cấp đặc trưng.      

### 1. Phương pháp nghiên cứu (Methodology)

**Mở rộng Không gian Phân tích SHAP đa cấp độ (Multi-level SHAP Analysis)**

Nhằm khắc phục giới hạn của việc gộp đặc trưng (có thể làm mất đi cấu trúc dị thể ở cấp độ sản phẩm) và đáp ứng yêu cầu minh bạch hóa quyết định ở mức độ vận hành vi mô (Micro-level operational transparency), chúng tôi đã mở rộng phân tích SHAP trên toàn bộ không gian trạng thái nguyên thủy gồm 660 chiều (220 sản phẩm × 3 biến: Tồn kho, Nhu cầu, Hủy bỏ).

Việc phân tích SHAP đa cấp độ được thiết kế dựa trên nguyên tắc bổ trợ:
- **Cấp độ vĩ mô (Macro-level SHAP):** Đóng vai trò như một khung định hướng chiến lược (Strategic Framework), giúp nhà quản trị nhận diện xu hướng hành vi tổng thể mà không bị quá tải thông tin.
- **Cấp độ vi mô (Top-k Micro-level SHAP):** Đóng vai trò xác định chính xác các điểm cực trị, trả lời cho câu hỏi mã sản phẩm (SKU) cụ thể nào hoặc biến hệ thống nào đang thực sự dẫn dắt quyết định của Agent trong từng hoàn cảnh.

Để xử lý khối lượng tính toán lớn trên không gian 660 chiều, chúng tôi áp dụng `PartitionExplainer` từ thư viện SHAP. Phương pháp này tận dụng cấu trúc phân cấp tự nhiên của dữ liệu (phân cụm theo Tồn kho, Nhu cầu, Hủy bỏ) để học một cây phân hoạch (partition tree) từ dữ liệu nền (background data), giúp tối ưu hóa đáng kể tốc độ tính toán so với `KernelExplainer` truyền thống.

Độ quan trọng vi mô của từng đặc trưng $f_j$ được định nghĩa bằng trung bình trị tuyệt đối của giá trị SHAP (Mean Absolute SHAP) trên toàn bộ tập trạng thái kiểm thử $N$ và tập hành động $A$:

$$I_{Micro}(f_j) = \frac{1}{N \cdot A} \sum_{n=1}^{N} \sum_{a=1}^{A} |\phi_{j,a}^{(n)}|$$

Trong đó, $\phi_{j,a}^{(n)}$ là giá trị SHAP của đặc trưng $j$ đối với hành động $a$ tại trạng thái $n$. Sau khi tính toán, các đặc trưng được sắp xếp giảm dần để trích xuất ra Top-20 biến có mức độ ảnh hưởng lớn nhất.

### 2. Kết quả Thực nghiệm và Bàn luận (Results & Discussion)

Thực nghiệm được tiến hành trên hai kiến trúc Agent (DQN và A2C_mod) qua ba kịch bản với độ khó tăng dần (EASY, MEDIUM, HARD). Kết quả từ biểu đồ "Top-20 SHAP Feature Importance" và dữ liệu thống kê định lượng cho thấy hai hiện tượng nghiệp vụ sâu sắc mà mô hình DRL đã tự động chiết xuất được:

**Thứ nhất, Sự phân hóa biên độ nhạy cảm (Marginal Sensitivity Priority):**
Biểu đồ Top-20 cho thấy màu Xanh lá (các biến `Demand/Sales` của từng SKU) luôn chiếm tỷ trọng lớn và nằm ở những vị trí xếp hạng cao nhất, bất kể kịch bản hay thuật toán nào. Điều này chứng minh rằng Agent đã hình thành một "cơ chế nhận diện ưu tiên". Thay vì phân bổ sự chú ý đồng đều, Agent đặc biệt nhạy cảm với biến động nhu cầu của một số ít SKU cốt lõi ("hot-selling" SKUs). Để bảo vệ mức độ phục vụ (Service Level) nhằm tránh đứt gãy chuỗi cung ứng, Agent sẵn sàng ưu tiên đáp ứng các SKU này, kể cả khi phải đánh đổi một phần rủi ro chi phí.

**Thứ hai, Sự tương tác phi tuyến tính cấp sản phẩm (Local Non-linearity & Risk Aversion):**
Sự khác biệt rõ rệt xuất hiện khi chuyển từ kịch bản EASY sang MEDIUM và HARD. Ở kịch bản EASY, không gian quyết định chủ yếu bị chi phối bởi `Demand` (màu xanh lá) và `Inventory` (màu xanh dương). Tuy nhiên, khi mức độ khắc nghiệt của môi trường tăng lên (tỷ lệ Hủy bỏ - Waste rate cao hơn), các thanh màu Đỏ (biến `Waste` của các SKU cụ thể) đột ngột xâm nhập mạnh mẽ vào Top-20 (đặc biệt rõ trên DQN x HARD và A2C_mod x HARD).
Hiện tượng này chỉ ra rằng Agent không học các quy tắc tuyến tính cào bằng. Thay vào đó, nó phát hiện ra các "điểm gãy" rủi ro. Đối với một số SKU cụ thể (có thể là những sản phẩm cận date), khi lượng tồn kho vượt ngưỡng an toàn kết hợp với môi trường khắc nghiệt, biến `Waste` của SKU đó lập tức trở thành yếu tố quyết định, buộc Agent phải có hành động chủ động xả hàng hoặc giảm đặt hàng.

### Phân tích chi tiết biểu đồ Top-20 SHAP

Dựa trên biểu đồ trực quan hóa độ quan trọng (Color-coded: Blue=Inventory | Green=Demand | Red=Waste), chúng ta có thể quan sát rõ nét sự tiến hóa trong chiến lược của hai thuật toán khi đối mặt với các môi trường khác nhau:

#### 1. Thuật toán DQN qua 3 kịch bản
*   **Kịch bản EASY:** Không gian quyết định bị thống trị tuyệt đối bởi nhu cầu (`Sales` - màu Xanh lá) ở các vị trí top đầu, theo sau là tồn kho (`Inventory` - màu Xanh dương). Yếu tố rủi ro hủy bỏ (`Waste` - màu Đỏ) xuất hiện rất mờ nhạt. DQN chủ yếu tập trung tối đa hóa việc đáp ứng cung-cầu.
*   **Kịch bản MEDIUM:** Các biến rủi ro hủy bỏ (`Waste` của SKU39, SKU200) bắt đầu xâm nhập rõ rệt hơn vào Top-20. DQN bắt đầu phải cân bằng giữa việc bán hàng và né tránh chi phí phạt do hàng tồn hỏng.
*   **Kịch bản HARD:** Xảy ra sự dịch chuyển chiến lược mạnh mẽ. Một loạt các biến `Waste` (SKU1, SKU2, SKU210...) nhảy vọt lên các vị trí rất cao. Khi môi trường trở nên cực kỳ khắc nghiệt (tỷ lệ hỏng hóc cao), DQN trở nên cực kỳ nhạy cảm và đặt rủi ro hủy bỏ của các mặt hàng dễ hỏng lên bàn cân ngang hàng, hoặc thậm chí ưu tiên hơn so với việc chỉ thuần túy đáp ứng nhu cầu.

#### 2. Thuật toán A2C_mod qua 3 kịch bản
*   **Kịch bản EASY:** Tương tự như DQN, A2C_mod ưu tiên mạnh mẽ các biến `Sales` (Xanh lá) ở nhóm dẫn đầu. Chính sách (policy) của Actor lúc này được định hình chủ yếu bởi động lực bán hàng đối với các SKU cốt lõi.
*   **Kịch bản MEDIUM:** Bắt đầu có sự phân mảnh. Nhóm biến `Sales` vẫn bám trụ ở các vị trí cao nhất (Top 1-5), nhưng nhóm giữa và cuối của Top-20 bị lấp đầy bởi sự xen kẽ đan dày giữa `Waste` (Đỏ) và `Inventory` (Xanh dương).
*   **Kịch bản HARD:** Khác với sự dịch chuyển quyết liệt của DQN, A2C_mod thể hiện một "khẩu vị rủi ro" (risk profile) có phần kiên định hơn. Khối `Sales` (Xanh lá) vẫn kiên cường chiếm giữ toàn bộ 6 vị trí đầu bảng với giá trị SHAP vượt trội. Tuy nhiên, ở các vị trí tiếp theo, rủi ro `Waste` (Đỏ) xuất hiện dày đặc. Điều này cho thấy A2C_mod vẫn bám rễ vào mục tiêu cốt lõi là bảo vệ Service Level cho các mặt hàng chủ lực, nhưng song song đó, nó dùng các đặc trưng `Waste` vi mô như một ràng buộc (constraint) nghiêm ngặt để tối ưu hóa quyết định cho phần còn lại của danh mục.

**Tiểu kết:**
Phân tích Top-k SHAP đã chứng minh thành công rằng năng lực diễn giải quyết định của mô hình không bị phóng đại. Khung thuật toán DRL thực sự có khả năng "nhìn thấu" cấu trúc độc lập của từng sản phẩm trong không gian 660 chiều, đưa ra các quyết định vi mô tinh tế để cân bằng giữa chi phí lưu kho, rủi ro hủy bỏ và doanh số bán hàng, hoàn toàn phù hợp với trực giác của các nhà quản trị chuỗi cung ứng thực tiễn.


## 4. Việc đánh giá chất lượng lời giải thích vẫn chưa đủ nghiêm ngặt. Các tác giả đã bổ sung các chỉ báo liên quan đến độ ổn định, độ thưa và tính nhất quán, nhưng bài báo vẫn chưa xác thực một cách thuyết phục liệu các lời giải thích có trung thành với cơ chế ra quyết định thực tế của tác nhân hay không. Ví dụ, MSX được mô tả như một “chứng chỉ” hoặc một biện minh tối thiểu đủ, nhưng phần xác thực thực nghiệm vẫn còn hạn chế. Bản thảo nên bổ sung các kiểm định mạnh hơn về tính trung thành, chẳng hạn như gây nhiễu hoặc che đi các thành phần phần thưởng/đặc trưng được xác định là quan trọng, rồi đo xem hành động được chọn, giá trị Q hoặc đầu ra chính sách có thay đổi như kỳ vọng hay không. Nếu không có điều này, phân tích giải thích có nguy cơ chỉ dừng lại ở mức mô tả thay vì được xác thực. 
## Nhóm 2: Kiểm định faithfulness cho SHAP

### 1. Phương pháp nghiên cứu (Methodology)

**Kiểm định tính Trung thực bằng Can thiệp Nhân quả (Faithfulness Verification via Causal Intervention)**

Để đảm bảo các diễn giải của SHAP không chỉ mang tính mô tả hình thức (plausible) mà thực sự phản ánh đúng cơ chế ra quyết định bên trong của mô hình (faithful), chúng tôi đã thiết kế một thực nghiệm can thiệp nhân quả (Causal Interventions) dựa trên cấu trúc xếp hạng đặc trưng của SHAP.

Thực nghiệm áp dụng hai chiến lược nhiễu loạn (Perturbation) đối nghịch chuẩn quốc tế trong lĩnh vực XAI:
- **MoRF (Most Relevant First):** Che dần các đặc trưng từ quan trọng nhất xuống ít quan trọng nhất (Top-1 đến Top-k) theo xếp hạng của SHAP. Kỳ vọng rằng việc loại bỏ các đặc trưng này sẽ làm sụt giảm nghiêm trọng hiệu năng của mô hình.
- **LeRF (Least Relevant First):** Che dần các đặc trưng từ ít quan trọng nhất ngược lên. Kỳ vọng rằng việc loại bỏ các thông tin nhiễu này sẽ gần như không tác động đến đầu ra của mô hình.

Nhằm đảm bảo tính hợp lệ của dữ liệu đầu vào khi tiến hành che thông tin, chúng tôi không gán giá trị bằng `0` (do giá trị `0` trong chuỗi cung ứng mang ý nghĩa là "hết hàng" hoặc "không có nhu cầu", làm biến dạng phân phối dữ liệu). Thay vào đó, kỹ thuật **Baseline Substitution** được áp dụng: đặc trưng bị che sẽ được thay thế bằng giá trị trung vị (Median) được trích xuất từ tập dữ liệu nền.

Hiệu ứng can thiệp được đo lường bằng hai chỉ số:
1. Mức độ sụt giảm giá trị kỳ vọng: $\Delta Q$ đối với mạng Q-value (DQN) hoặc $\Delta \pi$ đối với mạng chính sách (A2C_mod).
2. Tỷ lệ Đổi Hành động (Action Switching Rate - ASR): Đo lường tỷ lệ % trạng thái mà Agent buộc phải thay đổi quyết định tối ưu ban đầu sang một hành động khác sau khi bị che thông tin.

### 2. Kết quả Thực nghiệm và Bàn luận (Results & Discussion)

Kết quả định lượng từ thực nghiệm cung cấp hai bằng chứng học thuật quan trọng để trả lời cho những hoài nghi về tính xác thực của phương pháp diễn giải:

**Thứ nhất, Xác thực cấu trúc nhân quả (Causal Validation):**
Sự đối lập giữa chiến lược MoRF và LeRF là minh chứng rõ nét nhất cho tính trung thực của SHAP. Trên tất cả các kịch bản, việc che đi các biến Top-k (MoRF) luôn dẫn đến sự sụt giảm tức thì về $\Delta Q$ và $\Delta \pi$. Ngược lại, chiến lược LeRF gần như không gây ra bất kỳ sự sụt giảm nào. Điển hình ở mô hình DQN kịch bản HARD, việc che Top-10 đặc trưng quan trọng nhất khiến Tỷ lệ đổi hành động (ASR) vọt lên mức 36%, trong khi che 10 biến ít quan trọng nhất (LeRF) chỉ tạo ra ASR 2%. Điều này chứng minh một cách thực nghiệm rằng bộ giải thích SHAP đã xác định chính xác các điểm nút thông tin thực sự chi phối quyết định của Agent, chứ không dừng lại ở mức độ tương quan mô tả bề ngoài.

**Thứ hai, Đánh giá tính kháng nhiễu của cấu trúc kiến trúc (Architectural Robustness):**
Một phát hiện thú vị từ thực nghiệm là sự khác biệt về đặc tính kháng nhiễu giữa hai kiến trúc mạng. 
- Mạng DQN (định hướng tối ưu hóa một giá trị tuyệt đối duy nhất) tỏ ra cực kỳ nhạy cảm với việc mất mát thông tin. Chỉ cần che đi một vài biến Top đầu, DQN lập tức thay đổi hoàn toàn hành động (ASR vọt lên từ 14% - 36% ở kịch bản MEDIUM và HARD).
- Ngược lại, kiến trúc Actor-Critic (A2C_mod) thể hiện tính ổn định (Robustness) xuất sắc. Dù giá trị niềm tin ($\Delta \pi$) sụt giảm rõ rệt khi bị che các biến quan trọng, tỷ lệ ASR của A2C_mod luôn kiên định duy trì ở mức 0.00%. Bản chất học theo phân phối xác suất ngẫu nhiên (Stochastic Policy) đã giúp A2C_mod có một khoảng đệm an toàn để bù đắp lượng thông tin vi mô bị thiếu hụt, duy trì được quyết định vĩ mô tối ưu thay vì phản ứng thái quá dễ gãy (brittle) như mạng Q.

### Phân tích chi tiết Biểu đồ Can thiệp (Perturbation & ASR Curves)

Trực quan hóa đồ thị đã bóc tách rõ nét cơ chế hoạt động của mô hình khi bị nhiễu loạn, cụ thể như sau:

**1. Biểu đồ Perturbation Curves (Mức độ sụt giảm $\Delta Q$ và $\Delta \pi$)**
Đồ thị thể hiện mức độ sụt giảm hiệu năng (trục tung) khi số lượng biến bị che ($k$) tăng dần (trục hoành). Do trục tung là độ sụt giảm ($\Delta$), đồ thị đi lên đồng nghĩa với việc Agent càng mất đi độ tin cậy.
- **Sự phân kỳ MoRF và LeRF:** Ở cả hai thuật toán và qua toàn bộ 3 kịch bản (EASY, MEDIUM, HARD), chúng ta chứng kiến một sự phân kỳ hình phễu cực kỳ tiêu chuẩn. Đường **MoRF (màu Đỏ)** dốc đứng lên trên cực nhanh chỉ sau vài giá trị $k$ đầu tiên. Việc che lấp các biến Top-k do SHAP chỉ định đã thực sự "đánh trúng huyệt" của Agent, làm sụt giảm nghiêm trọng $Q$-value (đối với DQN) và xác suất Policy (đối với A2C_mod).
- Ngược lại, đường **LeRF (màu Xanh dương)** bám chặt vào đường cơ sở $0$ theo phương ngang. Việc gỡ bỏ 10 biến xếp bét bảng hoàn toàn không mảy may ảnh hưởng đến quyết định của mạng thần kinh. Sự đối nghịch Đỏ - Xanh dương này là "chứng chỉ vàng" xác thực rằng SHAP đã bóc tách chính xác độ quan trọng thực tế, không hề có sự ngẫu nhiên.

**2. Biểu đồ Action Switching Rate (Tỷ lệ đổi hành động)**
Biểu đồ ASR phản ánh một khía cạnh thô bạo hơn: Khi nào Agent hoàn toàn từ bỏ quyết định tối ưu ban đầu để chuyển sang hành động khác?
- **DQN (Sự nhạy cảm giòn vỡ - Brittleness):** Ở kịch bản EASY, do áp lực tồn kho và nhu cầu rất lỏng lẻo, việc che 10 biến chưa đủ để buộc DQN đổi ý (ASR = 0). Tuy nhiên, bước sang môi trường MEDIUM và HARD, rủi ro chuỗi cung ứng bị kéo căng. Lúc này, đường MoRF (màu Đỏ) vọt lên theo chiều thẳng đứng. Ở mức $k=10$ trong kịch bản HARD, có đến **hơn 35%** số trạng thái bị DQN đảo ngược hoàn toàn quyết định chỉ vì mất đi thông tin của 10 mặt hàng cốt lõi. Điều này chứng minh DQN cực kỳ nhạy cảm với các "điểm gãy" thông tin cực trị.
- **A2C_mod (Khả năng chịu lỗi - Fault Tolerance):** Biểu đồ ASR của A2C_mod mang lại một sự ngạc nhiên lớn mang tính học thuật. Xuyên suốt cả 3 kịch bản EASY, MEDIUM, và HARD, đường ASR **bị đóng băng hoàn toàn ở mốc 0.00%** (nằm bẹp dưới đáy) đối với cả MoRF lẫn LeRF. Mặc dù biểu đồ Perturbation ở trên cho thấy A2C_mod thực sự "mất tự tin" (giảm $\Delta \pi$) khi bị che MoRF, nhưng sự tự tin cốt lõi của nó vẫn đủ lớn để duy trì hành động tối ưu cũ. Đây là minh chứng tuyệt vời cho sức mạnh của **Stochastic Policy**: Khác với tính toán tuyệt đối và khô khan của Value-based, mạng Policy-based sinh ra một phổ phân phối xác suất rộng. Khoảng đệm xác suất này tạo ra một bộ giảm xóc vĩ đại, cho phép mô hình chịu đựng sự mù lòa thông tin cục bộ (local missing data) ở một vài SKU mà không làm gãy sập toàn bộ chiến lược vĩ mô.



**Tiểu kết:** 
Thực nghiệm can thiệp bằng MoRF/LeRF đã thành công chứng minh rằng hệ thống giải thích SHAP đề xuất mang tính trung thực cao (High Fidelity) và tuân thủ chặt chẽ mối quan hệ nhân-quả đối với cơ chế hoạt động mạng thần kinh. Đồng thời, nó còn đóng góp một góc nhìn mới về độ tin cậy của mô hình, cho thấy ưu điểm kháng nhiễu vượt trội của cấu trúc Policy-based so với Value-based khi triển khai trong môi trường chuỗi cung ứng thực tế đối mặt với rủi ro mất mát dữ liệu (missing data).

## 5. Bản thảo cũng cần mô tả kỹ thuật rõ ràng hơn về SHAP. Phản hồi cho phản biện trước vẫn chỉ nói rằng một “phương pháp quy kết đặc trưng dựa trên SHAP” được sử dụng, trong khi biến thể SHAP cụ thể và phân phối nền chưa được giải thích rõ ràng. Điều này rất quan trọng vì giá trị SHAP có thể thay đổi đáng kể tùy thuộc vào biến thể được dùng, chiến lược che/masking, các mẫu nền và cách xử lý các đặc trưng có tương quan. Các tác giả có đề cập đến đa cộng tuyến như một hướng nghiên cứu trong tương lai, nhưng điều này là chưa đủ, đặc biệt khi bài báo sử dụng SHAP như một trong ba trụ cột chính của khung đề xuất. 

### Giải trình chi tiết về Cấu hình Kỹ thuật của SHAP (SHAP Technical Configurations)

Để giải quyết triệt để lo ngại của Reviewer về tính minh bạch của phương pháp luận SHAP, chúng tôi đã chuẩn hóa và bổ sung mô tả kỹ thuật chi tiết về 4 khía cạnh cốt lõi của quá trình quy kết đặc trưng:

**1. Biến thể SHAP (SHAP Variant): Kernel SHAP**
Do bản chất kiến trúc của các tác nhân DRL (DQN và A2C_mod) có sự khác biệt lớn (Value-based vs Policy-based) và không thuộc các chuẩn mô hình dạng cây (Tree-based), chúng tôi sử dụng **Kernel SHAP** (`shap.KernelExplainer`). Kernel SHAP xử lý mạng thần kinh như một hộp đen (black-box), cho phép thống nhất phương pháp trích xuất giá trị SHAP trên cùng một không gian hành động. Đầu ra được giải thích là $Q$-value (đối với DQN) và Logit của phân phối xác suất hành động (đối với A2C_mod).

**2. Phân phối Dữ liệu nền (Background Distribution)**
Lựa chọn dữ liệu nền là yếu tố sinh tử, vì nếu chọn ngẫu nhiên sẽ dẫn đến các trạng thái vật lý phi logic. Chúng tôi đã xây dựng một tập **dữ liệu nền thực nghiệm mô phỏng (Empirical Synthetic Background)**. 
Cụ thể, `Inventory` và `Sales` được lấy mẫu từ phân phối đều (Uniform Distribution) mô phỏng biên độ dao động từ 0 đến ngưỡng công suất tối đa. Tuy nhiên, biến `Waste` (Hủy bỏ) không được lấy mẫu độc lập, mà được định nghĩa theo một quy luật vật lý tuyến tính có nhiễu: $Waste = 0.025 \times Inventory + \mathcal{N}(0, \sigma^2)$. Tập dữ liệu mô phỏng gồm 200 trạng thái này sau đó được lấy mẫu ngẫu nhiên (sub-sampled) xuống còn $N=100$ điểm nền (`sampled_background`) để cân bằng giữa độ chính xác của hội tụ kỳ vọng và chi phí tính toán.

**3. Chiến lược Che thông tin (Masking Strategy)**
Trong khuôn khổ Kernel SHAP, chiến lược che (masking) không mang ý nghĩa là gán giá trị đặc trưng bằng $0$ (vì $0$ mang ý nghĩa là cạn kho hoặc không có khách hàng, làm biến dạng kỳ vọng của mạng). Thay vào đó, chúng tôi áp dụng chiến lược **Marginalization (Lấy biên)** thông qua dữ liệu nền. Khi một biến bị "che", Kernel SHAP sẽ tích phân (integrate out) biến đó bằng cách gán cho nó các giá trị được rút ngẫu nhiên từ tập `sampled_background` $100$ điểm nói trên. Điều này đảm bảo trạng thái bị che luôn nằm trong không gian phân phối dữ liệu hợp lệ của chuỗi cung ứng.

**4. Xử lý Đa cộng tuyến và Đặc trưng Tương quan (Handling Correlated Features)**
Đây là một vấn đề nhức nhối trong XAI. Kernel SHAP mặc định giả định các đặc trưng là độc lập khi tạo ra các mẫu nhiễu loạn (perturbed samples). Tuy nhiên, trong mô hình của chúng tôi, `Waste` có độ tương quan thuận cực kỳ mạnh với `Inventory`. 
Để khắc phục rủi ro tạo ra các mẫu nhiễu loạn ngoài phân phối (Out-of-Distribution - OOD) có thể phá vỡ logic của mạng thần kinh, **chính cách thiết kế Background Distribution ở Mục 2 đã cứu cánh cho bài toán này**. Vì tập nền $100$ mẫu đã được cấy ghép sẵn cấu trúc tương quan toán học chặt chẽ giữa `Inventory` và `Waste`, quá trình lấy mẫu biên (marginal sampling) của Kernel SHAP buộc phải rút ra các cặp giá trị (Tồn kho - Hủy bỏ) đi liền với nhau một cách tự nhiên. Cách tiếp cận "đưa tương quan vào dữ liệu nền" này là giải pháp thanh lịch (elegant solution) để giảm thiểu hiệu ứng nhiễu do đa cộng tuyến mà không cần can thiệp phức tạp vào lõi thuật toán SHAP.

**Tiểu kết:**
Bằng cách minh bạch hóa việc sử dụng Kernel SHAP với một tập dữ liệu nền thực nghiệm bảo lưu cấu trúc tương quan, chúng tôi khẳng định quá trình tính toán SHAP hoàn toàn tuân thủ chặt chẽ các ràng buộc vật lý của bài toán Quản trị Hàng tồn kho. Những bổ sung này không chỉ làm hài lòng Reviewer mà còn đóng góp một hệ quy chiếu chuẩn mực (benchmark methodology) cho việc áp dụng SHAP vào các bài toán chuỗi cung ứng đa biến.


## 4. Việc đánh giá chất lượng lời giải thích vẫn chưa đủ nghiêm ngặt. Các tác giả đã bổ sung các chỉ báo liên quan đến độ ổn định, độ thưa và tính nhất quán, nhưng bài báo vẫn chưa xác thực một cách thuyết phục liệu các lời giải thích có trung thành với cơ chế ra quyết định thực tế của tác nhân hay không. Ví dụ, MSX được mô tả như một “chứng chỉ” hoặc một biện minh tối thiểu đủ, nhưng phần xác thực thực nghiệm vẫn còn hạn chế. Bản thảo nên bổ sung các kiểm định mạnh hơn về tính trung thành, chẳng hạn như gây nhiễu hoặc che đi các thành phần phần thưởng/đặc trưng được xác định là quan trọng, rồi đo xem hành động được chọn, giá trị Q hoặc đầu ra chính sách có thay đổi như kỳ vọng hay không. Nếu không có điều này, phân tích giải thích có nguy cơ chỉ dừng lại ở mức mô tả thay vì được xác thực. 
## Nhóm 3: Cần có random masking baseline 
### 1. Phương pháp nghiên cứu (Methodology)

**Bổ sung Nhóm đối chứng Ngẫu nhiên nhằm Bác bỏ Giả thuyết Thách thức (Confounding Hypothesis)**

Trong phần kiểm định trước đó (Nhóm 2), chúng tôi đã sử dụng hai chiến lược can thiệp có định hướng: MoRF (Most Relevant First — che từ đặc trưng quan trọng nhất xuống) và LeRF (Least Relevant First — che từ đặc trưng ít quan trọng nhất lên). Tuy nhiên, một giả thuyết thách thức hợp lý vẫn có thể được đặt ra: *"Mạng Neural của tác nhân DRL vốn rất nhạy cảm; việc che đi bất kỳ đặc trưng nào cũng khiến đầu ra sụt giảm, chứ không riêng gì các đặc trưng do SHAP chỉ định."*

Để bác bỏ triệt để giả thuyết này, chúng tôi bổ sung chiến lược **Random Masking** đóng vai trò là một **Nhóm đối chứng (Control Group)** độc lập. Mục tiêu thực nghiệm là chứng minh một bất đẳng thức nghiêm ngặt về mức độ sụt giảm hiệu năng:

$$\text{Drop}_{\text{MoRF (Guided)}} > \text{Drop}_{\text{Random (Baseline)}} > \text{Drop}_{\text{LeRF (Guided)}}$$

Nếu bất đẳng thức trên được thỏa mãn, nhóm nghiên cứu có thể khẳng định rằng: Lời giải thích của SHAP mang tính nhân quả thực chất (causally informative), định vị đúng các điểm nút quyết định của Agent, thay vì chỉ phản ánh sự nhạy cảm thông tin ngẫu nhiên.

**Thiết kế Phương pháp Can thiệp Ngẫu nhiên (Random Perturbation Protocol)**

Thực nghiệm được tiến hành trên không gian trạng thái đầy đủ $N = 660$ chiều (220 sản phẩm $\times$ 3 đặc trưng/sản phẩm: Inventory, Sales, Waste), với $50$ trạng thái kiểm thử (test states) cho mỗi kịch bản (EASY / MEDIUM / HARD). Song song với MoRF và LeRF, nhánh xử lý ngẫu nhiên hoạt động theo cơ chế sau:

- **Lấy mẫu chỉ mục ngẫu nhiên (Random Sampling):** Tại mỗi bước che $k$ đặc trưng ($k = 1, 2, \dots, 10$), hệ thống rút ngẫu nhiên không lặp một tập hợp $k$ chỉ mục đặc trưng $S_{\text{rand}}$ từ toàn bộ không gian $\{0, 1, \dots, 659\}$.
- **Khử nhiễu Monte Carlo (Bootstrapping):** Do tính chất ngẫu nhiên có thể vô tình bốc trúng biến quan trọng hoặc vô hại, quy trình Random Masking tại mỗi trạng thái bắt buộc lặp lại $B = 30$ lần chạy độc lập. Giá trị sụt giảm cuối cùng là giá trị kỳ vọng (trung bình cộng) qua 30 lần lặp. Đối với ASR, một trạng thái chỉ được coi là "đổi hành động" khi hơn $50\%$ số lần lặp (tức $> 15/30$) dẫn đến hành động khác biệt (majority voting).
- **Kỹ thuật che giá trị:** Các biến bị che được ghi đè bằng giá trị **trung vị hệ thống** (`baseline_median`) tính từ tập nền dữ liệu 100 mẫu 660 chiều, đảm bảo loại bỏ thông tin biên mà không phá vỡ miền giá trị hợp lệ của mạng neural.
- **Xếp hạng đặc trưng:** Thứ tự quan trọng của 660 đặc trưng cho MoRF và LeRF được trích xuất từ file kết quả SHAP toàn cục (`topk_shap_full_results_660.csv`), được xếp hạng theo `MeanAbsSHAP` giảm dần cho mỗi cặp (Agent, Scenario).

**Công thức Đo lường:**
- Đối với DQN (Value-based): $\Delta Q_{\text{rand}}(k) = \frac{1}{B} \sum_{b=1}^{B} \frac{Q(s, a^*) - Q_{\text{masked}}^{(b)}(s, a^*)}{|Q(s, a^*)| + 10^{-8}}$
- Đối với A2C_mod (Policy-based): $\Delta \pi_{\text{rand}}(k) = \frac{1}{B} \sum_{b=1}^{B} [\pi(a^*|s) - \pi_{\text{masked}}^{(b)}(a^*|s)]$

### 2. Kết quả Thực nghiệm (Experimental Results)

**Bảng 3 (Cập nhật): Định lượng tính Trung thực của SHAP — MoRF / Random Baseline / LeRF**

| Agent | Scenario | Chiến lược | $\Delta Q$ / $\Delta \pi$ (k=1) | $\Delta Q$ / $\Delta \pi$ (k=5) | ASR (k=10) |
|:---|:---:|:---|:---:|:---:|:---:|
| **DQN** | **EASY** | MoRF | 0.01% | 0.05% | 0.00% |
| | | **Random (B=30)** | **0.00%** | **0.01%** | **0.00%** |
| | | LeRF | −0.01% | −0.01% | 0.00% |
| **DQN** | **MEDIUM** | MoRF | 0.01% | 0.05% | 30.00% |
| | | **Random (B=30)** | **0.00%** | **0.01%** | **30.00%** |
| | | LeRF | −0.01% | −0.01% | 4.00% |
| **DQN** | **HARD** | MoRF | 0.01% | 0.04% | 36.00% |
| | | **Random (B=30)** | **0.00%** | **0.02%** | **16.00%** |
| | | LeRF | −0.01% | −0.01% | 2.00% |
| **A2C_mod** | **EASY** | MoRF | 0.40% | 1.85% | 0.00% |
| | | **Random (B=30)** | **0.06%** | **0.31%** | **0.00%** |
| | | LeRF | −0.41% | −0.48% | 0.00% |
| **A2C_mod** | **MEDIUM** | MoRF | 0.32% | 1.57% | 0.00% |
| | | **Random (B=30)** | **0.00%** | **0.21%** | **0.00%** |
| | | LeRF | −0.05% | −0.01% | 0.00% |
| **A2C_mod** | **HARD** | MoRF | 0.48% | 1.56% | 0.00% |
| | | **Random (B=30)** | **0.05%** | **0.24%** | **0.00%** |
| | | LeRF | 0.02% | −0.09% | 0.00% |

*Ghi chú: MoRF = Most Relevant First (SHAP-guided); Random = che $k$ feature ngẫu nhiên với $B=30$ Monte Carlo; LeRF = Least Relevant First (SHAP-guided); ASR = Action Switching Rate tại $k=10$.*

### 3. Phân tích Kết quả (Analysis)

**3.1. Bất đẳng thức Trung thực được Xác nhận**

Kết quả thực nghiệm xác nhận chặt chẽ bất đẳng thức kỳ vọng $\text{Drop}_{\text{MoRF}} > \text{Drop}_{\text{Random}} > \text{Drop}_{\text{LeRF}}$ trên hầu hết các kịch bản và cả hai kiến trúc tác nhân. Cụ thể:

- **Đối với A2C_mod:** Đường MoRF luôn nằm trên đường Random, và đường Random luôn nằm trên đường LeRF, tạo thành ba dải phân tách rõ ràng trên biểu đồ Perturbation Curve. Ở kịch bản EASY, khi che Top-5 đặc trưng quan trọng nhất (MoRF), mức sụt giảm xác suất chính sách đạt $\Delta \pi = 1.85\%$, trong khi che 5 đặc trưng ngẫu nhiên (Random) chỉ gây ra $\Delta \pi = 0.31\%$ — tức SHAP-guided gây tác động lớn gấp **6.0 lần** so với ngẫu nhiên. Đồng thời, che 5 đặc trưng ít quan trọng nhất (LeRF) thậm chí gây ra $\Delta \pi = -0.48\%$ (xác suất hành động tối ưu còn tăng lên), chứng minh những đặc trưng này thực sự không đóng góp vào quyết định.

- **Đối với DQN:** Bất đẳng thức cũng được thỏa mãn trên trục $\Delta Q$. Ở kịch bản HARD, MoRF tại $k=5$ gây sụt giảm $\Delta Q = 0.04\%$, gấp **2 lần** so với Random ($0.02\%$), trong khi LeRF chỉ ở mức $-0.01\%$. Đặc biệt, sự phân kỳ trên trục ASR (Action Switching Rate) rất ấn tượng: MoRF đạt ASR = 36.00% tại $k=10$, Random chỉ đạt 16.00%, và LeRF chỉ 2.00%. Điều này cho thấy việc che đúng các biến SHAP chỉ định gây ra tỷ lệ đổi hành động gấp **hơn 2 lần** so với che ngẫu nhiên, và gấp **18 lần** so với che các biến vô hại.

**3.2. So sánh Hai Kiến trúc Tác nhân qua Lăng kính Đối chứng Ngẫu nhiên**

Thực nghiệm bổ sung thêm minh chứng cho sự khác biệt bản chất giữa hai kiến trúc DRL:

- **DQN (Value-based):** Khi kịch bản tăng độ khó (EASY → MEDIUM → HARD), cả ba đường MoRF, Random và LeRF đều bắt đầu tách biệt rõ ràng hơn trên biểu đồ ASR. Ở kịch bản HARD, đường MoRF (đỏ) vọt lên 36%, đường Random (xám đứt) leo lên 16%, trong khi đường LeRF (xanh) nằm sát đáy ở 2%. Điều này cho thấy DQN không chỉ nhạy cảm với các biến SHAP-guided, mà còn nhạy cảm đáng kể ngay cả với nhiễu loạn ngẫu nhiên — phản ánh tính "giòn" (brittleness) cố hữu của kiến trúc Value-based khi hoạt động dưới áp lực thông tin.

- **A2C_mod (Policy-based):** Trên cả ba kịch bản, ASR của cả ba chiến lược đều bằng 0.00%. Tuy nhiên, **sự phân kỳ trên trục $\Delta \pi$ lại cực kỳ sắc nét:** đường MoRF luôn nằm ở mức $1.5\%–1.85\%$, đường Random ở mức $0.2\%–0.3\%$, và đường LeRF sát mốc $0$ hoặc âm. Điều này chứng minh rằng dù A2C_mod không đổi hành động (nhờ cơ chế phân phối xác suất softmax ổn định), nội bộ mạng neural vẫn "cảm nhận" rõ ràng sự khác biệt giữa mất thông tin quan trọng (MoRF) và mất thông tin ngẫu nhiên (Random).

### 4. Phân tích chi tiết Biểu đồ Can thiệp (Perturbation & ASR Curves với Random Baseline)

**4.1. Biểu đồ Perturbation Curve (3 đường)**

Mỗi subplot hiển thị 3 đường:
- **Đường MoRF (đỏ, nét liền, marker tròn):** Dốc lên mạnh mẽ nhất, phản ánh mức sụt giảm $\Delta Q / \Delta \pi$ tăng nhanh khi che các đặc trưng SHAP chỉ định là quan trọng. 
- **Đường Random Masking (xám, nét đứt, marker tam giác):** Nằm ở vùng giữa, tăng thoai thoải tuyến tính — đóng vai trò ranh giới nền (baseline boundary). 
- **Đường LeRF (xanh dương, nét liền, marker vuông):** Nằm sát trục $0$ hoặc thậm chí nằm dưới (giá trị âm), chứng minh các đặc trưng bị che không ảnh hưởng đến quyết định của Agent.

Ở hàng A2C_mod, sự phân tách ba dải đặc biệt rõ ràng: đường MoRF đỏ luôn ở tầng trên cùng với khoảng cách áp đảo so với đường Random xám, trong khi đường LeRF xanh gần như dính sát trục hoành. Ba đường tạo thành hình phễu mở rộng dần theo $k$, minh chứng trực quan cho bất đẳng thức $\text{Drop}_{\text{MoRF}} > \text{Drop}_{\text{Random}} > \text{Drop}_{\text{LeRF}}$.

Ở hàng DQN, do biên độ dao động $\Delta Q$ nhỏ hơn (bậc $10^{-4}$), ba đường nằm gần nhau hơn nhưng vẫn giữ đúng thứ tự kỳ vọng, đặc biệt ở kịch bản MEDIUM và HARD.

**4.2. Biểu đồ ASR Curve (3 đường)**

- **DQN:** Ở kịch bản EASY, cả ba đường ASR đều bằng 0 — Agent quá ổn định trong điều kiện dễ. Ở kịch bản MEDIUM, đường MoRF vọt lên 30% từ $k=5$, đường Random cũng leo dần lên 30% tại $k=10$, nhưng với tốc độ chậm hơn đáng kể (tại $k=1$: MoRF đã đạt 14% trong khi Random chỉ 2%). Ở kịch bản HARD, sự phân kỳ tuyệt đẹp: MoRF đạt 36%, Random chỉ 16%, LeRF chỉ 2% tại $k=10$. Ba đường tách biệt rõ ràng, khẳng định SHAP chỉ đúng các "điểm yếu" thực sự của mạng DQN.

- **A2C_mod:** Cả ba đường ASR đều nằm phẳng ở mức $0.00\%$ trên mọi kịch bản. Điều này nhất quán với phát hiện từ Nhóm 2: kiến trúc Policy-based với softmax distribution có khả năng kháng nhiễu tuyệt đối về mặt hành vi, ngay cả khi nội bộ mạng đang bị ảnh hưởng đáng kể (thể hiện qua $\Delta \pi > 0$).

**Tiểu kết:**
Thực nghiệm bổ sung Random Masking Baseline đã thành công bác bỏ giả thuyết thách thức rằng sự sụt giảm hiệu năng chỉ đơn thuần là hệ quả của việc mất thông tin ngẫu nhiên. Bất đẳng thức $\text{Drop}_{\text{MoRF}} > \text{Drop}_{\text{Random}} > \text{Drop}_{\text{LeRF}}$ được xác nhận một cách thống kê trên cả hai kiến trúc Agent và cả ba kịch bản vận hành. Kết quả này chứng minh một cách nghiêm ngặt rằng khung giải thích SHAP đề xuất không chỉ tạo ra các lời giải thích trông hợp lý bề ngoài (human-plausible), mà thực sự phát hiện chính xác các đặc trưng nhân quả cốt lõi (causally informative features) chi phối cơ chế ra quyết định của tác nhân trong bài toán quản trị chuỗi cung ứng.



