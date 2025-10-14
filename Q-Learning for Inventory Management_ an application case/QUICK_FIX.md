# 🚨 Quick Fix: FileNotFoundError

## ❌ Lỗi bạn gặp

```
FileNotFoundError: [Errno 2] No such file or directory: 'models/q_table_inventory.pkl'
```

## ✅ Nguyên nhân

Bạn đang cố load model nhưng **chưa train lần nào** nên file chưa được tạo ra.

---

## 🔧 Giải pháp (ĐÃ SỬA)

### Đã sửa ở Cell 4:

```python
USE_PRETRAINED = False  # ← Đã đổi thành False
```

**Giờ bạn chỉ cần:**

1. **Chạy tuần tự Cell 1 → 9** (train lần đầu)
   - Cell 1-6: Setup environment
   - Cell 7: Training (~5-10 phút) 
   - Cell 8-9: Save model ✅
   
2. **File được tạo**: `models/q_table_inventory.pkl`

3. **Lần sau** (load nhanh):
   - Đổi `USE_PRETRAINED = True`
   - Chạy Cell 1-6, skip 7-9
   - Tiết kiệm 5-10 phút! ⚡

---

## 📋 Checklist lần đầu

- [x] Cell 4: `USE_PRETRAINED = False` ✅ (đã sửa)
- [ ] Chạy Cell 1: Import numpy, pandas
- [ ] Chạy Cell 2: Import pickle, os, datetime
- [ ] Chạy Cell 3: Khởi tạo tham số
- [ ] Chạy Cell 4: Load model (sẽ báo "Train mới")
- [ ] Chạy Cell 6: Định nghĩa môi trường
- [ ] Chạy Cell 7: **Training** ⏱️ ~5-10 phút
- [ ] Chạy Cell 8-9: **Lưu model** → File được tạo! ✅
- [ ] Chạy Cell 10-19: Xem kết quả

---

## 🔄 Lần sau (sau khi đã có file)

### Cách 1: Load model (Nhanh ⚡)

```python
# Cell 4: Đổi thành
USE_PRETRAINED = True
```

- Chạy Cell 1-6 → Load model (1 giây)
- **SKIP Cell 7-9** (không cần train!)
- Chạy Cell 10-19 → Xem kết quả

### Cách 2: Train lại (Chậm ⏱️)

```python
# Cell 4: Giữ nguyên
USE_PRETRAINED = False
```

- Train lại từ đầu (nếu đổi hyperparameters)

---

## 🎯 Tóm tắt

| Tình huống | USE_PRETRAINED | Hành động |
|------------|----------------|-----------|
| Lần đầu chạy | `False` | Train → Save |
| Đã có file model | `True` | Load nhanh |
| Muốn train lại | `False` | Train lại |

---

## 💡 Tip

Sau khi train xong lần đầu, bạn có thể:

1. **Backup file model**:
   ```powershell
   copy models\q_table_inventory.pkl models\q_table_backup.pkl
   ```

2. **Thử nghiệm hyperparameters khác**:
   - Đổi alpha, gamma trong Cell 3
   - Train lại → Lưu với tên khác
   - So sánh performance

3. **Share với người khác**:
   - Gửi file `test2.ipynb` + thư mục `models/`
   - Họ set `USE_PRETRAINED = True`
   - Không cần train lại!

---

**✅ Vấn đề đã được giải quyết!**

Giờ bạn có thể chạy notebook mà không gặp lỗi nữa.
