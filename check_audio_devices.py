"""
Script kiểm tra và liệt kê các audio devices
Giúp xác định đúng microphone để tránh ghi âm system audio
"""
import pyaudio
import sys

# Fix encoding cho Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')

def list_audio_devices():
    """Liệt kê tất cả audio input devices"""
    p = pyaudio.PyAudio()
    
    print("=" * 80)
    print("DANH SACH CAC AUDIO DEVICES")
    print("=" * 80)
    
    default_input = p.get_default_input_device_info()
    print(f"\n[DEFAULT INPUT DEVICE]:")
    print(f"   Index: {default_input['index']}")
    print(f"   Name: {default_input['name']}")
    print(f"   Max Input Channels: {default_input['maxInputChannels']}")
    
    print(f"\n[TAT CA DEVICES]:\n")
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        
        # Chỉ hiển thị input devices
        if info['maxInputChannels'] > 0:
            is_default = " **DEFAULT**" if i == default_input['index'] else ""
            
            # Phát hiện loại device
            name_lower = info['name'].lower()
            if 'stereo mix' in name_lower or 'what u hear' in name_lower or 'wave out' in name_lower:
                device_type = "[!] SYSTEM AUDIO (khong dung cho mic)"
            elif 'microphone' in name_lower or 'mic' in name_lower:
                device_type = "[OK] MICROPHONE (nen dung)"
            elif 'line in' in name_lower:
                device_type = "[~] LINE IN"
            else:
                device_type = "[?] UNKNOWN"
            
            print(f"Index {i}{is_default}")
            print(f"   Name: {info['name']}")
            print(f"   Type: {device_type}")
            print(f"   Max Input Channels: {info['maxInputChannels']}")
            print(f"   Default Sample Rate: {int(info['defaultSampleRate'])} Hz")
            print()
    
    p.terminate()
    
    print("=" * 80)
    print("HUONG DAN:")
    print("=" * 80)
    print("1. Tim device co type '[OK] MICROPHONE' trong danh sach tren")
    print("2. Ghi nho Index cua no (vi du: Index 2)")
    print("3. Mo file config.json")
    print("4. Tim dong: \"input_device_index\": null")
    print("5. Thay doi thanh: \"input_device_index\": 2  (so index ban tim duoc)")
    print("6. Luu file va chay lai ung dung")
    print()
    print("[!] QUAN TRONG: KHONG dung 'Stereo Mix' hoac 'What U Hear'")
    print("    Cac device nay ghi am system audio (nhac, video) thay vi microphone!")
    print("=" * 80)

if __name__ == "__main__":
    try:
        list_audio_devices()
    except Exception as e:
        print(f"[!] Loi: {e}")
        print("\nDam bao ban da cai: pip install pyaudio")
