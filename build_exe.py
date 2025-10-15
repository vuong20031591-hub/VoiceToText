"""
Build script để tạo file .exe cho Voice to Text Application
"""
# -*- coding: utf-8 -*-
import os
import sys
import io

# Force UTF-8 encoding for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import shutil
import subprocess
from pathlib import Path

def clean_build():
    """Dọn dẹp thư mục build cũ"""
    print("[1/4] Don dep thu muc build cu...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   [OK] Da xoa {dir_name}")
    
    # Xóa file .spec cũ
    spec_files = [f for f in os.listdir('.') if f.endswith('.spec')]
    for spec_file in spec_files:
        os.remove(spec_file)
        print(f"   [OK] Da xoa {spec_file}")

def install_pyinstaller():
    """Cài đặt PyInstaller nếu chưa có"""
    print("[2/4] Kiem tra PyInstaller...")
    
    try:
        import PyInstaller
        print("   [OK] PyInstaller da duoc cai dat")
    except ImportError:
        print("   [INFO] Dang cai dat PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("   [OK] Da cai dat PyInstaller")

def create_exe():
    """Tạo file .exe (API keys embedded)"""
    print("🔨 Đang tạo file .exe với API keys embedded...")
    
    # PyInstaller command
    # NOTE: API keys đã được hardcode trong app.py
    # PyInstaller v6.0+ không hỗ trợ --key encryption nữa
    cmd = [
        "python", "-m", "PyInstaller",
        "--onefile",                    # Tạo một file exe duy nhất
        "--windowed",                   # Không hiển thị console window
        "--name=VoiceToText",           # Tên file exe
        "--add-data=config.json;.",     # Thêm config.json (optional backup)
        "--hidden-import=groq",
        "--hidden-import=requests",
        "--hidden-import=customtkinter",
        "--hidden-import=pynput",
        "--hidden-import=pyaudio",
        "--hidden-import=pyperclip",
        "--hidden-import=numpy",
        "--collect-all=customtkinter",
        "--noupx",                      # Không dùng UPX để khó reverse hơn
        "main.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("    Đã tạo file .exe thành công!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"    Lỗi tạo file .exe: {e}")
        return False

def optimize_exe():
    """Tối ưu file .exe"""
    print("⚡ Tối ưu file .exe...")
    
    exe_path = Path("dist/VoiceToText.exe")
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"   📏 Kích thước file: {size_mb:.1f} MB")
        
        # Copy config.json vào thư mục dist
        if os.path.exists("config.json"):
            shutil.copy2("config.json", "dist/")
            print("   ✅ Đã copy config.json")
        
        # Tạo thư mục release
        release_dir = Path("release")
        release_dir.mkdir(exist_ok=True)
        
        # Copy file exe và config vào release
        shutil.copy2(exe_path, release_dir / "VoiceToText.exe")
        shutil.copy2("config.json", release_dir / "config.json")
        shutil.copy2("README.md", release_dir / "README.md")
        
        print(f"  File release đã sẵn sàng trong thư mục: {release_dir}")
        print(f"  Chạy ứng dụng: {release_dir / 'VoiceToText.exe'}")
        
        return True
    else:
        print("    Không tìm thấy file .exe")
        return False

def main():
    """Main build function"""
    print("BẮT ĐẦU BUILD VOICE TO TEXT APPLICATION")
    print("=" * 50)
    
    try:
        # 1. Dọn dẹp
        clean_build()
        print()
        
        # 2. Cài đặt PyInstaller
        install_pyinstaller()
        print()
        
        # 3. Tạo exe
        if create_exe():
            print()
            
            # 4. Tối ưu
            if optimize_exe():
                print()
                print("BUILD THÀNH CÔNG!")
                print("=" * 50)
                print("File .exe đã được tạo trong thư mục 'release'")
                print("Chạy: release/VoiceToText.exe")
                print("Cấu hình: release/config.json")
                print()
                print("   HƯỚNG DẪN SỬ DỤNG:")
                print("   1. Chạy VoiceToText.exe")
                print("   2. Nhấn giữ Ctrl+Alt để ghi âm")
                print("   3. Nói vào microphone")
                print("   4. Thả hotkey để nhận dạng")
                print("   5. Văn bản tự động dán!")
            else:
                print(" Lỗi tối ưu file .exe")
                return False
        else:
            print(" Lỗi tạo file .exe")
            return False
            
    except Exception as e:
        print(f" Lỗi build: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
