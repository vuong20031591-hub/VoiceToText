# Voice to Text - Vietnamese Speech Recognition

<div align="center">



**Ứng dụng nhận dạng giọng nói tiếng Việt tốc độ cao với AI**

[Tính năng](#tính-năng) • [Demo](#demo) • [Cài đặt](#cài-đặt) • [Sử dụng](#sử-dụng) • [Đóng góp](#đóng-góp)

</div>

---

## Demo


### Screenshots


---

## Tính năng

### Core Features
- **Nhận dạng giọng nói tiếng Việt** với độ chính xác cao (Groq Whisper)
- **Tốc độ cực nhanh** - Kết quả trong 0.5-1 giây
- **Multi API keys rotation** - Tự động chuyển key khi hết quota
- **Hotkey recording** - Giữ `Ctrl+Alt` để ghi âm, thả để dừng
- **Auto paste** - Text tự động dán vào ứng dụng đang focus

### GUI & UX
- **Modern overlay GUI** - Giao diện trong suốt, đẹp mắt
- **Wave visualization** - Hiển thị dạng sóng real-time
- **Entrance animation** - Hiệu ứng slide up & fade in
- **Bottom-center positioning** - Vị trí tối ưu, không che chắn

### Technical
- **Audio enhancement** - Giảm nhiễu, tăng chất lượng (có thể tắt)
- **Text correction** - Sửa lỗi dấu, ngữ pháp tiếng Việt
- **Standalone executable** - File .exe duy nhất, không cần cài đặt
- **Config-based** - Dễ dàng tùy chỉnh qua file JSON

---

## Yêu cầu hệ thống

- **OS:** Windows 10/11
- **Python:** 3.8+ (chỉ cần nếu build từ source)
- **RAM:** 2GB+
- **Microphone:** Bất kỳ (USB, built-in, Bluetooth)
- **Internet:** Cần kết nối (API calls)

---

## Cài đặt

### Option 1: Sử dụng file .exe có sẵn (Khuyến nghị)

1. **Download** file `.exe` từ [Releases](../../releases)
2. **Giải nén** (nếu có)
3. **Chạy** `VoiceToText.exe`
4. **Nhấn giữ** `Ctrl+Alt` và nói
5. **Thả phím** để kết thúc → Text tự động dán!

### Option 2: Build từ source code

#### 1. Clone repository
```bash
git clone https://github.com/vuong20031591-hub/VoiceToText.git
cd VoiceToText
```

#### 2. Cài đặt dependencies
```bash
# Tự động cài đặt
install_requirements.bat

# Hoặc thủ công
pip install -r requirements.txt
```

#### 3. Cấu hình API keys

**Lấy API keys miễn phí:**
- Truy cập: https://console.groq.com/keys
- Tạo tài khoản (free)
- Generate API key

**Cấu hình:**
```bash
# Mở file config.json
notepad config.json
```

Thêm API keys vào:
```json
{
  "stt": {
    "api_keys": [
      "gsk_YOUR_API_KEY_HERE"
    ]
  }
}
```

#### 4. Chạy ứng dụng
```bash
# Cách 1: Script clean
run_clean.bat

# Cách 2: Python trực tiếp
python main.py
```

#### 5. Build file .exe (Optional)
```bash
python build_exe.py
```

File .exe sẽ được tạo trong thư mục `release/`

---

## Sử dụng

### Ghi âm cơ bản
1. **Mở** ứng dụng muốn nhập text (Notepad, Word, Browser...)
2. **Click** vào vị trí cần nhập text
3. **Nhấn giữ** `Ctrl+Alt`
4. **Nói** vào microphone
5. **Thả phím** → Text tự động xuất hiện!

### Hotkeys
| Phím | Chức năng |
|------|-----------|
| `Ctrl+Alt` (giữ) | Bắt đầu ghi âm |
| `Ctrl+Alt` (thả) | Dừng & nhận dạng |
| `Ctrl+Shift+C` | Thoát ứng dụng |

### Tùy chỉnh
Chỉnh sửa `config.json` để thay đổi:
- **Hotkey**: Phím tắt khác
- **Sample rate**: Chất lượng audio
- **Text correction**: Bật/tắt sửa lỗi
- **GUI**: Kích thước, vị trí, theme
- **Audio enhancement**: Giảm nhiễu, tăng âm

```json
{
  "hotkey": {
    "key": "ctrl+alt"  // Đổi thành "ctrl+shift", "alt+space"...
  },
  "audio": {
    "sample_rate": 16000  // 16000 = nhanh, 44100 = chất lượng cao
  }
}
```

---

## Development

### Cấu trúc project
```
VoiceToText/
├── main.py                 # Entry point
├── config.json             # Configuration
├── requirements.txt        # Dependencies
│
├── src/
│   ├── core/
│   │   ├── app.py         # Main application logic
│   │   └── hotkey_manager.py
│   │
│   ├── gui/
│   │   └── overlay.py     # GUI overlay
│   │
│   ├── services/
│   │   ├── groq_stt_service.py  # STT API
│   │   └── text_corrector.py    # Text correction
│   │
│   └── utils/
│       ├── config_loader.py
│       └── logger_setup.py
│
├── build_exe.py           # Build script
└── release/               # Built executables
```

### Tech Stack
- **STT Engine:** Groq Whisper Large V3
- **GUI Framework:** CustomTkinter
- **Audio:** PyAudio + NumPy
- **Hotkeys:** pynput
- **Clipboard:** pyperclip
- **Build:** PyInstaller

---

## Đóng góp

### Chúng tôi cần bạn!

Dự án này được phát triển với mục tiêu **mã nguồn mở** và **miễn phí**. Mọi đóng góp đều được chào đón!

### Cách đóng góp

#### 1. Báo lỗi (Bug Report)
- Tạo [Issue mới](../../issues/new) với template Bug Report
- Mô tả chi tiết: OS, Python version, log errors
- Attach screenshot/video nếu có

#### 2. Đề xuất tính năng (Feature Request)
- Tạo [Issue mới](../../issues/new) với template Feature Request
- Giải thích tại sao cần feature này
- Mô tả use case cụ thể

#### 3. Pull Request
```bash
# Fork repository
git clone https://github.com/vuong20031591-hub/VoiceToText.git
cd VoiceToText

# Tạo branch mới
git checkout -b feature/ten-tinh-nang

# Code & commit
git add .
git commit -m "Add: Mo ta thay doi"

# Push & tạo PR
git push origin feature/ten-tinh-nang
```

**Coding Guidelines:**
- Follow existing code style
- Add comments cho logic phức tạp
- Test kỹ trước khi commit
- Update README nếu thay đổi API

#### 4. Cải thiện Documentation
- Sửa typo, làm rõ hướng dẫn
- Thêm examples, tutorials
- Dịch sang tiếng Anh (English README)

#### 5. Design & UI/UX
- Thiết kế icon, logo
- Cải thiện GUI
- Tạo video hướng dẫn

### Ý tưởng cho Contributors

#### Tính năng đang cần:
- [ ] **MacOS support** (hiện chỉ có Windows)
- [ ] **Linux support**
- [ ] **Offline mode** (local Whisper model)
- [ ] **Multi-language** (English, Chinese...)
- [ ] **Custom vocabulary** (thuật ngữ chuyên ngành)
- [ ] **Voice commands** (thực thi lệnh bằng giọng nói)
- [ ] **Cloud sync settings**
- [ ] **Mobile app** (Android/iOS remote control)

#### Cải thiện hiện có:
- [ ] Tối ưu tốc độ nhận dạng
- [ ] Giảm kích thước .exe
- [ ] Thêm unit tests
- [ ] CI/CD pipeline
- [ ] Auto-update mechanism
- [ ] Better error handling
- [ ] Accessibility features (cho người khuyết tật)

---

## Roadmap

### Version 2.1 (Q4 2024)
- [ ] MacOS/Linux support
- [ ] Offline mode
- [ ] Settings GUI
- [ ] Auto-update

### Version 3.0 (Q1 2025)
- [ ] Multi-language support
- [ ] Voice commands
- [ ] Cloud sync
- [ ] Mobile companion app

---

## License

Dự án được phát hành dưới **MIT License** - xem file [LICENSE](LICENSE) để biết thêm chi tiết.

**Tóm tắt:**
- ✅ Sử dụng thương mại
- ✅ Chỉnh sửa
- ✅ Phân phối
- ✅ Sử dụng riêng tư
- ❌ Không bảo hành

---

## Liên hệ & Hỗ trợ

### Cộng đồng
- **Discussion:** [GitHub Discussions](../../discussions)
- **Issues:** [GitHub Issues](../../issues)
- **Email:** voicetotext@example.com

### Contributors
Cảm ơn những người đã đóng góp cho dự án!

<!-- Contributors sẽ tự động hiển thị -->
<a href="../../graphs/contributors">
  <img src="https://contrib.rocks/image?repo=vuong20031591-hub/VoiceToText" />
</a>

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=vuong20031591-hub/VoiceToText&type=Date)](https://star-history.com/#vuong20031591-hub/VoiceToText&Date)

---

## Ủng hộ dự án

Nếu bạn thấy dự án hữu ích, hãy:
- **Star** repository này
- **Share** với bạn bè, đồng nghiệp
- **Report bugs** để cải thiện
- **Contribute code** để phát triển
- **Write tutorials** để giúp người khác

Mỗi star là động lực để chúng tôi phát triển dự án tốt hơn!

---

<div align="center">

**Made with love by the VoiceToText Community**

[Back to top](#voice-to-text---vietnamese-speech-recognition)

</div>
