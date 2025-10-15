# Hướng dẫn đóng góp cho Voice to Text

Cảm ơn bạn đã quan tâm đến việc đóng góp cho dự án!

## Mục lục

- [Code of Conduct](#code-of-conduct)
- [Làm thế nào để đóng góp](#làm-thế-nào-để-đóng-góp)
- [Quy trình phát triển](#quy-trình-phát-triển)
- [Coding Standards](#coding-standards)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

Dự án này tuân thủ [Code of Conduct](CODE_OF_CONDUCT.md). Khi tham gia, bạn cam kết tôn trọng cộng đồng và người khác.

---

## Làm thế nào để đóng góp

### Báo cáo lỗi

Trước khi tạo bug report:
- Kiểm tra [Issues hiện có](../../issues) để tránh trùng lặp
- Sử dụng phiên bản mới nhất
- Thử chạy với clean config

Khi tạo bug report, bao gồm:
- **Mô tả rõ ràng** về lỗi
- **Các bước tái hiện** (step-by-step)
- **Kết quả mong đợi** vs **Kết quả thực tế**
- **Screenshots/Videos** (nếu có)
- **Environment:**
  - OS: Windows 10/11
  - Python version: 3.x.x
  - App version: x.x.x
- **Log files** (nếu có)

### Đề xuất tính năng

Feature requests rất được hoan nghênh! Bao gồm:
- **Mô tả tính năng** rõ ràng
- **Use case** cụ thể
- **Lợi ích** cho người dùng
- **Mockups/Sketches** (nếu về UI)

### Code Contribution

1. **Fork** repository
2. **Clone** về máy local
3. **Tạo branch** mới: `git checkout -b feature/amazing-feature`
4. **Code & Test**
5. **Commit**: `git commit -m 'Add: Amazing feature'`
6. **Push**: `git push origin feature/amazing-feature`
7. **Tạo Pull Request**

---

## Quy trình phát triển

### 1. Setup môi trường

```bash
# Clone repository
git clone https://github.com/vuong20031591-hub/VoiceToText.git
cd VoiceToText

# Tạo virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Cài dependencies
pip install -r requirements.txt

# Copy config mẫu
copy config.example.json config.json
```

### 2. Chạy trong development mode

```bash
# Clean run
run_clean.bat

# Hoặc
python main.py
```

### 3. Test changes

```bash
# Manual testing
# - Test với nhiều loại audio
# - Test hotkeys
# - Test edge cases

# Automated testing (TODO)
# pytest tests/
```

### 4. Build & Test .exe

```bash
python build_exe.py
# Test file .exe trong release/
```

---

## Coding Standards

### Python Style Guide

Tuân thủ **PEP 8** với một số điều chỉnh:

```python
# Imports
import standard_library
import third_party
from local_module import something

# Constants
MAX_RECORDING_TIME = 30.0
DEFAULT_SAMPLE_RATE = 16000

# Functions/Methods
def process_audio(audio_data: bytes) -> str:
    """
    Process audio and return transcription.
    
    Args:
        audio_data: Raw audio bytes
        
    Returns:
        Transcribed text
    """
    pass

# Classes
class AudioProcessor:
    """Handle audio processing tasks."""
    
    def __init__(self, config: dict):
        self.config = config
```

### Naming Conventions

- **Variables/Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`

### Comments

```python
# Single-line comment cho logic đơn giản

def complex_function():
    """
    Docstring cho functions/classes phức tạp.
    
    Bao gồm:
    - Mô tả ngắn gọn
    - Args, Returns, Raises (nếu có)
    - Examples (nếu cần)
    """
    # Inline comments cho logic khó hiểu
    result = self._calculate_something()  # Tại sao cần tính
    return result
```

### File Structure

```python
"""
Module docstring - Mô tả module
"""
# 1. Standard library imports
import os
import sys

# 2. Third-party imports
import numpy as np

# 3. Local imports
from .utils import helper

# 4. Constants
CONSTANT_VALUE = 100

# 5. Classes
class MyClass:
    pass

# 6. Functions
def my_function():
    pass

# 7. Main execution
if __name__ == "__main__":
    main()
```

---

## Commit Messages

Tuân thủ **Conventional Commits**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: Tính năng mới
- **fix**: Sửa lỗi
- **docs**: Thay đổi documentation
- **style**: Format code (không ảnh hưởng logic)
- **refactor**: Refactor code
- **perf**: Cải thiện performance
- **test**: Thêm/sửa tests
- **chore**: Maintain tasks (build, dependencies...)

### Examples

```bash
# Feature
feat(stt): Add multi-language support

# Bug fix
fix(audio): Fix microphone not working on Windows 11

# Documentation
docs(readme): Update installation guide

# Performance
perf(audio): Optimize audio processing speed by 50%

# Refactor
refactor(gui): Simplify overlay rendering logic
```

---

## Pull Request Process

### 1. Trước khi tạo PR

- [ ] Code tuân thủ style guide
- [ ] Test kỹ trên local
- [ ] Update documentation (nếu cần)
- [ ] Rebase với main branch mới nhất
- [ ] Không có merge conflicts

### 2. PR Title & Description

**Title format:**
```
<type>: <short description>
```

**Description template:**
```markdown
## Changes
- Change 1
- Change 2

## Purpose
Explain why this change is needed

## Testing
How did you test this?

## Screenshots
(if UI changes)

## Checklist
- [ ] Code follows style guide
- [ ] Self-reviewed
- [ ] Tested locally
- [ ] Documentation updated
```

### 3. Review Process

- Maintainers sẽ review trong vòng 1-3 ngày
- Trả lời comments và thực hiện requested changes
- Sau khi approved → merge vào main

### 4. Sau khi merge

- Branch của bạn sẽ được xóa
- Changes sẽ có trong release tiếp theo
- Tên bạn sẽ được thêm vào Contributors!

---

## Resources

### Docs
- [Python PEP 8](https://www.python.org/dev/peps/pep-0008/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [CustomTkinter Docs](https://customtkinter.tomschimansky.com/)

### Tools
- **Formatter**: `black`, `autopep8`
- **Linter**: `pylint`, `flake8`
- **Type Checker**: `mypy`

---

## Questions?

Nếu có thắc mắc:
- Tạo [Discussion](../../discussions)
- Email: voicetotext@example.com
- [Issues](../../issues) (cho bugs/features)

---

**Cảm ơn bạn đã đóng góp!**

Together, we make Voice to Text better for everyone!
