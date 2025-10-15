"""
Voice to Text Application - Entry Point
"""
from src.core import VoiceToTextApp


def main():
    """Main function"""
    print("=" * 60)
    print("VOICE TO TEXT APPLICATION")
    print("Ung dung chuyen doi giong noi thanh van ban")
    print("=" * 60)
    
    try:
        app = VoiceToTextApp()
        app.start()
    except Exception as e:
        print(f"Loi khoi dong: {e}")
        input("Nhan Enter de thoat...")


if __name__ == "__main__":
    main()
