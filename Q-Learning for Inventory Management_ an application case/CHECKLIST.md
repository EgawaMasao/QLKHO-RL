# Checklist: Cách sử dụng test2.ipynb

## Scenario 1: Train model lần đầu

- [ ] Mở file `test2.ipynb`
- [ ] **Cell 4**: Đổi `USE_PRETRAINED = False`
- [ ] Chạy Cell 1-3 (Import & khởi tạo tham số)
- [ ] Chạy Cell 6 (Định nghĩa môi trường)
- [ ] Chạy Cell 7 (Training - chờ ~5-10 phút)
- [ ] Chạy Cell 8 (Lưu model) → File lưu vào `models/q_table_inventory.pkl`
- [ ] Chạy Cell 10 (Trích xuất policy)
- [ ] Chạy Cell 11 (Xem learning curve)
- [ ] Chạy Cell 12-19 (Evaluation & visualization)
- [ ] ✅ Xong! Model đã được lưu

---

## Scenario 2: Load model đã train (NHANH)

- [ ] Mở file `test2.ipynb`
- [ ] **Cell 4**: Để `USE_PRETRAINED = True` (mặc định)
- [ ] Chạy Cell 1-3 (Import & khởi tạo)
- [ ] Chạy Cell 4 (Load model - 1 giây) → Thấy thông báo "✅ Đã load model"
- [ ] **SKIP Cell 6-9** (Không cần train!)
- [ ] Chạy Cell 10 (Trích xuất policy từ Q đã load)
- [ ] Chạy Cell 11 (Xem learning curve từ history đã lưu)
- [ ] Chạy Cell 12-19 (Evaluation & visualization)
- [ ] Xong! Tiết kiệm 5-10 phút

---

## Scenario 3: So sánh hyperparameters

### Lần 1: Train với alpha=0.2, gamma=0.9
- [ ] **Cell 3**: Đặt `alpha = 0.2`, `gamma = 0.9`
- [ ] **Cell 4**: Đặt `USE_PRETRAINED = False`
- [ ] Train (Cell 6-7)
- [ ] **Cell 8**: Sửa tên file: `save_model(..., "models/q_alpha02_gamma09.pkl")`
- [ ] Ghi lại cost: `__________ €/ngày`

### Lần 2: Train với alpha=0.5, gamma=0.5
- [ ] **Cell 3**: Đặt `alpha = 0.5`, `gamma = 0.5`
- [ ] **Cell 4**: Đặt `USE_PRETRAINED = False`
- [ ] Train (Cell 6-7)
- [ ] **Cell 8**: Sửa tên file: `save_model(..., "models/q_alpha05_gamma05.pkl")`
- [ ] Ghi lại cost: `__________ €/ngày`

### So sánh
- [ ] Load từng model và so sánh `final_avg_cost`
- [ ] Chọn model tốt nhất
- [ ] Copy file model tốt nhất → `models/q_table_production.pkl`

---

## Scenario 4: Demo cho người khác

- [ ] Đảm bảo đã train và lưu model trước
- [ ] Share file `test2.ipynb` + thư mục `models/`
- [ ] Hướng dẫn họ:
  - [ ] Chạy Cell 1-4 (Import + Load model)
  - [ ] SKIP Cell 6-9 (Training)
  - [ ] Chạy Cell 10-19 (Xem kết quả)
- [ ] Giải thích về learning curve (Cell 11)
- [ ] Giải thích về policy (Cell 13-14)

---

## Troubleshooting

### "File models/q_table_inventory.pkl không tồn tại"
**Nguyên nhân**: Chưa train lần nào  
**Giải pháp**:
- [ ] Đặt `USE_PRETRAINED = False`
- [ ] Chạy training (Cell 6-7)
- [ ] Chạy save (Cell 8)

### "ModuleNotFoundError: No module named 'pickle'"
**Nguyên nhân**: Python quá cũ (pickle có sẵn từ Python 2.6+)  
**Giải pháp**:
- [ ] Kiểm tra Python version: `python --version`
- [ ] Nên dùng Python 3.7+

###  Learning curve trống rỗng
**Nguyên nhân**: Load model cũ nhưng chưa train lại  
**Giải pháp**:
- [ ] Đó là learning curve từ lần train trước (đã lưu trong file)
- [ ] Hoàn toàn bình thường!

### Muốn train lại từ đầu
**Giải pháp**:
- [ ] Xóa file cũ (hoặc đổi tên file save)
- [ ] Đặt `USE_PRETRAINED = False`
- [ ] Chạy lại training

---

##  Quick Reference

| Task | Command/Cell |
|------|--------------|
| Import libraries | Cell 1-2 |
| Khởi tạo tham số | Cell 3 |
| Load model cũ | Cell 4 (USE_PRETRAINED=True) |
| Train mới | Cell 6-7 (USE_PRETRAINED=False) |
| Lưu model | Cell 8 |
| Xem learning curve | Cell 11 |
| Xem policy | Cell 13-14 |
| Đánh giá performance | Cell 15 |
| Mô phỏng 30 ngày | Cell 16 |
| Vẽ biểu đồ tồn kho | Cell 18 |
| Vẽ biểu đồ chi phí | Cell 19 |

---

##  Files tạo ra

```
models/
├── q_table_inventory.pkl     ← Model chính (1-2 KB)
├── q_table_demo.pkl          ← Model demo
└── q_*.pkl                   ← Các versions khác
```

---

## Expected Output

### Cell 4 (Load model)
```
Đã load model từ: models/q_table_inventory.pkl
   - Q-table shape: (41, 2)
   - Training date: 2025-10-14 23:30:56
   - Final avg cost: 2458.32 €/episode
   - Hyperparameters: alpha=0.2, gamma=0.9, epsilon=0.1

Đã restore toàn bộ model và parameters!
   → Có thể skip phần training và đi thẳng đến evaluation.
```

### Cell 8 (Save model)
```
Đã lưu model vào: models/q_table_inventory.pkl
   - Q-table shape: (41, 2)
   - Final avg cost: 2458.32 €/episode
   - Training time: 2025-10-14 23:45:12
```

### Cell 11 (Learning curve stats)
```
Thống kê chi phí:
   - Episode đầu tiên: 2687.54 €
   - Episode cuối cùng: 2458.32 €
   - Trung bình 100 episode cuối: 2461.23 €
   - Chi phí thấp nhất: 2341.12 € (episode 847)
   - Chi phí cao nhất: 2687.54 € (episode 1)
```

---

## Đọc thêm

- [ ] `MODEL_USAGE.md` - Hướng dẫn chi tiết
- [ ] `IMPROVEMENTS_SUMMARY.md` - Tổng quan cải tiến
- [ ] `demo_model_persistence.py` - Demo script

---

**✅ Checklist này giúp bạn:**
- Biết chính xác phải làm gì
- Không bỏ sót bước nào
- Troubleshoot khi gặp lỗi
- Dùng đúng workflow cho từng tình huống

**Mục tiêu**: Tiết kiệm thời gian, tăng hiệu quả!
