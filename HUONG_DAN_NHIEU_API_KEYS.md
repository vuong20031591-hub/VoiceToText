# HƯỚNG DẪN SỬ DỤNG NHIỀU API KEYS VỚI AUTO-ROTATION

## Mục đích

Khi một API key **hết quota** (giới hạn số lần request trong ngày), ứng dụng sẽ **TỰ ĐỘNG** chuyển sang sử dụng API key tiếp theo, không bị gián đoạn.

---

## Giới hạn Groq API (Free Tier)

Mỗi API key miễn phí của Groq có giới hạn:
- **14,400 requests/ngày**
- **30 requests/phút**

→ Nếu bạn dùng nhiều, cần nhiều keys để không bị gián đoạn!

---

## Cách cấu hình

### CÁCH 1: Dùng 1 API key (Mặc định)

```json
{
    "stt": {
        "provider": "groq",
        "api_key": "gsk_XXXXXXXXXXXXXX",
        ...
    }
}
```

### CÁCH 2: Dùng NHIỀU API keys (Auto-Rotation)

```json
{
    "stt": {
        "provider": "groq",
        "api_keys": [
            "gsk_Key1XXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "gsk_Key2XXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "gsk_Key3XXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "gsk_Key4XXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "gsk_Key5XXXXXXXXXXXXXXXXXXXXXXXXXXX"
        ],
        ...
    }
}
```

**LƯU Ý:** 
- Nếu có **CẢ** `api_key` và `api_keys`, cả hai đều được dùng
- Ưu tiên: Biến môi trường → `api_key` → `api_keys`

---

## Cách hoạt động

### Khi gọi API:

1. **Bước 1:** Dùng API key đầu tiên (hoặc key hiện tại)
2. **Bước 2:** Nếu nhận lỗi `429` (Quota exceeded):
   - In thông báo: `⚠️ API key #1 đã hết quota (429)`
   - Tự động chuyển sang key tiếp theo
   - In thông báo: `🔄 Chuyển sang API key #2`
3. **Bước 3:** Thử lại với key mới
4. **Lặp lại** cho đến khi:
   - Thành công
   - HOẶC đã thử hết tất cả keys

### Xử lý lỗi:

| Lỗi | Mã | Xử lý |
|-----|-----|-------|
| Hết quota | 429 | Chuyển sang key khác |
| Key không hợp lệ | 401 | Chuyển sang key khác |
| Lỗi khác | ... | Dừng, báo lỗi |

---

## Ví dụ thực tế

### Ví dụ 1: Có 3 keys, key đầu hết quota

```
ĐANG GHI ÂM...
Dừng ghi âm - Đang xử lý...
Đang nhận dạng giọng nói...
Gọi Groq STT...

API key #1 đã hết quota (429)
Chuyển sang API key #2 (gsk_AbCd1234EfGh5678...)
Nhận dạng thành công với API key #2

Kết quả: 'xin chào bạn khỏe không'
Đang dán văn bản...
```

### Ví dụ 2: Tất cả keys đều hết quota

```
ĐANG GHI ÂM...
Dừng ghi âm - Đang xử lý...
Đang nhận dạng giọng nói...
Gọi Groq STT...

API key #1 đã hết quota (429)
Chuyển sang API key #2 (gsk_...)
API key #2 đã hết quota (429)
Chuyển sang API key #3 (gsk_...)
API key #3 đã hết quota (429)

Lỗi: Tất cả API keys đều hết quota! Vui lòng đợi hoặc thêm key mới
```

---

## Cách lấy nhiều API keys

### Phương pháp 1: Tạo nhiều keys trong 1 tài khoản

1. Truy cập: https://console.groq.com/keys
2. Đăng nhập
3. Tạo key mới (Create API Key)
4. Copy key và lưu lại
5. Lặp lại để tạo thêm keys

**Giới hạn:** Groq có thể giới hạn số key/tài khoản

### Phương pháp 2: Tạo nhiều tài khoản (Không khuyến khích)

1. Dùng email khác nhau
2. Đăng ký tài khoản mới
3. Lấy API key
4. Thêm vào `api_keys`

**Chú ý:** Kiểm tra Terms of Service của Groq về việc tạo nhiều tài khoản

---

## Lợi ích

- **Không bị gián đoạn** khi một key hết quota
- **Tự động chuyển đổi** không cần can thiệp
- **Tăng giới hạn** request lên gấp N lần (N = số keys)
- **Dễ quản lý** tất cả ở một chỗ
- **Phù hợp** cho ứng dụng sử dụng nhiều  

---

## Công thức tính quota tổng

```
Tổng requests/ngày = Số keys × 14,400
```

**Ví dụ:**
- 1 key: **14,400** requests/ngày
- 3 keys: **43,200** requests/ngày
- 5 keys: **72,000** requests/ngày
- 10 keys: **144,000** requests/ngày

---

## Bảo mật

**QUAN TRỌNG:**

1. **KHÔNG** commit `config.json` có API keys lên GitHub công khai
2. **KHÔNG** chia sẻ API keys công khai
3. Nếu keys bị lộ:
   - Truy cập: https://console.groq.com/keys
   - Xóa (revoke) tất cả keys bị lộ
   - Tạo keys mới
   - Cập nhật `config.json`

4. Nếu chia sẻ source code:
   ```json
   {
       "stt": {
           "api_keys": null  // ← Set về null
       }
   }
   ```
   Hướng dẫn người khác tự lấy keys

---

## Tips & Tricks

### Tip 1: Kiểm tra key nào đang dùng

Khi chạy ứng dụng, xem log:
```
Đã tải 3 API key(s)
   → Hỗ trợ auto-rotation khi hết quota
```

### Tip 2: Test các keys

Thêm keys vào config và chạy thử:
```bash
python main.py
```

Xem có thông báo lỗi về key nào không.

### Tip 3: Dùng cả biến môi trường + config

```bash
# Set biến môi trường
set GROQ_API_KEY=gsk_KeyFromEnv...

# Config
{
    "api_keys": ["gsk_Key1...", "gsk_Key2..."]
}
```

→ Sẽ có tổng **3 keys** (1 từ env + 2 từ config)

### Tip 4: Rotation thủ công

Keys sẽ được thử theo thứ tự trong mảng. Để ưu tiên key nào, đặt nó lên đầu:

```json
{
    "api_keys": [
        "gsk_KeyUuTien...",      // ← Dùng đầu tiên
        "gsk_KeyDuPhong1...",    // ← Dùng khi key 1 hết
        "gsk_KeyDuPhong2..."     // ← Dùng khi key 2 hết
    ]
}
```

---

## Xử lý lỗi thường gặp

### Lỗi: "Thiếu API key"

**Nguyên nhân:** Không có key nào được cấu hình

**Giải pháp:**
```json
{
    "stt": {
        "api_keys": ["gsk_YourKey..."]  // ← Thêm ít nhất 1 key
    }
}
```

### Lỗi: "Tất cả API keys đều hết quota"

**Nguyên nhân:** Tất cả keys đã dùng hết quota ngày

**Giải pháp:**
1. **Đợi đến ngày mai** (quota reset 00:00 UTC)
2. **HOẶC** thêm thêm keys mới
3. **HOẶC** upgrade lên Groq Pro

### Lỗi: "API key #X không hợp lệ (401)"

**Nguyên nhân:** Key đã bị revoke hoặc không đúng

**Giải pháp:**
1. Kiểm tra lại key tại: https://console.groq.com/keys
2. Xóa key không hợp lệ khỏi `api_keys`
3. Thêm key mới nếu cần

---

## Monitoring

Để theo dõi usage của từng key:

1. Truy cập: https://console.groq.com/usage
2. Chọn từng API key
3. Xem charts về:
   - Requests/ngày
   - Quota còn lại
   - Lịch sử sử dụng

---

## Checklist setup hoàn chỉnh

- [ ] Lấy ít nhất 2-3 API keys từ Groq
- [ ] Thêm vào `config.json` → `api_keys`
- [ ] Chạy thử `python main.py`
- [ ] Kiểm tra log có hiện "Đã tải X API key(s)"
- [ ] Test ghi âm vài lần
- [ ] Build .exe nếu muốn phân phối
- [ ] Backup `config.json` (nhưng KHÔNG commit lên Git)

---

## Tóm tắt

| Tính năng | Trước | Sau |
|-----------|-------|-----|
| Số keys | 1 | Không giới hạn |
| Khi hết quota | Dừng, báo lỗi | Tự động chuyển key khác |
| Giới hạn/ngày | 14,400 requests | 14,400 × N requests |
| Can thiệp thủ công | Cần | Không cần |

**→ Giờ bạn có thể yên tâm sử dụng nhiều mà không lo bị gián đoạn!**
