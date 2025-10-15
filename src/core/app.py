"""
Voice to Text Application - Main application logic
"""
import json
import logging
import os
import threading
import time
import tempfile
import wave
import queue
from typing import Optional

try:
    import pyaudio
    import numpy as np
    import pyperclip
    import customtkinter as ctk
except ImportError as e:
    print(f"[ERROR] Missing library: {e}")
    import sys
    sys.exit(1)

from ..services import GroqSTTService, VietnameseTextCorrector
from ..gui import ModernVoiceOverlay
from .hotkey_manager import HotkeyManager


class VoiceToTextApp:
    """Ứng dụng Voice to Text hoàn chỉnh trong một file"""
    
    def __init__(self):
        """Khởi tạo ứng dụng"""
        self.config = self._load_config()
        self._setup_logging()
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("[START] Initializing Voice to Text Application")
        
        # Audio recording
        self.audio = None
        self.stream = None
        self.is_recording = False
        self.audio_data = []
        self.recording_thread = None
        
        # Speech recognition - Chỉ dùng Groq STT
        self.remote_stt = None
        
        # Hotkey handling - SIMPLE TOGGLE MODE
        self.record_key = self.config.get('hotkey', {}).get('key', 'f9')
        self.exit_key = self.config.get('hotkey', {}).get('exit_key', 'f10')
        self.hotkey_manager = HotkeyManager(self.record_key, self.exit_key)

        # Exit sequence tracking
        self.exit_sequence = []
        self.exit_sequence_timeout = time.time()
        
        # GUI
        self.gui_enabled = self.config.get('gui', {}).get('show_overlay', True)
        self.root = None
        self.overlay = None
        
        # State
        self.is_running = False
        self.user_stopped_recording = False  # Track if user manually stopped
        self.should_hide_gui = False  # Flag to hide GUI from main thread

        # GUI queue for thread-safe communication
        self.gui_queue = queue.Queue()

        # Audio visualization
        self.current_audio_level = 0
        self.total_audio_energy = 0
        self.audio_samples_count = 0

        # Text correction
        self.text_corrector = None

        # Chống dán trùng lặp
        self._last_paste_text = ""
        self._last_paste_at = 0.0

        self._initialize()
    
    def _load_config(self) -> dict:
        """Tải cấu hình"""
        default_config = {
            "stt": {
                "provider": "groq",
                "api_base": "https://api.groq.com/openai/v1",
                "model": "whisper-large-v3",
                "language": "vi",
                "api_key_env": "GROQ_API_KEY",
                "api_key": None,
                "api_keys": [
                    "gsk_xxx",
                    "gsk_xxx",
                    "gsk_xxx",
                    "gsk_xxx",
                    "gsk_xxx"
                ],
                "timeout": 30
            },
            "hotkey": {
                "key": "ctrl+alt",
                "exit_key": "ctrl+shift+c"
            },
            "audio": {
                "sample_rate": 16000,
                "channels": 1,
                "chunk_size": 2048,
                "format": "int16",
                "input_device_index": None,
                "silence_threshold": 150,
                "silence_duration": 3.0,
                "max_recording_time": 30.0,
                "min_recording_time": 1.0,
                "noise_reduction": False,
                "auto_gain": False,
                "voice_activity_detection": False,
                "audio_enhancement": {
                    "enabled": False,
                    "normalize_volume": False,
                    "reduce_noise": False,
                    "enhance_speech": False,
                    "apply_filter": False
                }
            },
            "text_input": {
                "method": "paste",
                "typing_delay": 0.01
            },
            "logging": {
                "level": "WARNING",
                "show_console": False
            },
            "gui": {
                "show_overlay": True,
                "overlay_position": "center",
                "auto_hide_delay": 0.0,
                "theme": "light",
                "window_width": 250,
                "window_height": 150,
                "transparency": 0.95,
                "animation_speed": 0.05,
                "pulse_effect": True,
                "wave_visualization": True
            },
            "text_correction": {
                "enabled": True,
                "method": "dictionary",
                "show_original": False,
                "confidence_threshold": 0.9,
                "fix_tone_marks": True,
                "fix_grammar": False,
                "fix_homophones": False,
                "normalize_text": True,
                "smart_capitalization": False,
                "context_correction": False,
                "vietnamese_specific": {
                    "fix_dialects": False,
                    "standardize_spelling": True,
                    "correct_common_errors": True,
                    "apply_vietnamese_rules": False
                },
                "advanced_features": {
                    "semantic_correction": False,
                    "phrase_level_correction": False,
                    "context_aware_fixes": False
                }
            }
        }
        
        try:
            # Tìm config.json theo thứ tự ưu tiên:
            # 1. Working directory (để user có thể override)
            # 2. PyInstaller bundle (embedded trong .exe)
            # 3. Default config (hardcoded)
            
            config_path = None
            
            # Check working directory first
            if os.path.exists("config.json"):
                config_path = "config.json"
                print("[OK] Found config in working directory")
            # Check PyInstaller bundle
            elif getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                bundled_config = os.path.join(sys._MEIPASS, 'config.json')
                if os.path.exists(bundled_config):
                    config_path = bundled_config
                    print("[OK] Found config in PyInstaller bundle")
            
            # Load config if found
            if config_path:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"[OK] Loaded config from {config_path}")
                # Merge với default config
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
                
        except Exception as e:
            print(f"[WARNING] Config load error: {e}")
        
        print("[INFO] Using default config")
        return default_config
    
    def _setup_logging(self):
        """Thiết lập logging"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO').upper())
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Console handler
        if log_config.get('show_console', True):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logging.getLogger().addHandler(console_handler)
        
        # File handler
        file_handler = logging.FileHandler('voice_to_text.log', encoding='utf-8')
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)
        
        logging.getLogger().setLevel(log_level)
    
    def _initialize(self):
        """Khởi tạo các thành phần"""
        try:
            print("[CONFIG] Initializing components...")
            
            # Khởi tạo audio
            print("[AUDIO] Initializing audio...")
            try:
                self.audio = pyaudio.PyAudio()
                print("[OK] Audio initialized")
            except Exception as audio_error:
                print(f"[ERROR] Audio init error: {audio_error}")
                print("[TIP] Gợi ý giải quyết:")
                print("   1. Kiểm tra microphone đã được kết nối")
                print("   2. Kiểm tra driver audio")
                print("   3. Chạy ứng dụng với quyền Administrator")
                print("   4. Cài đặt lại: pip install pyaudio")
                self.audio = None
                raise audio_error
            
            # Khởi tạo Groq STT
            print("[AI] Initializing Groq STT...")
            self._init_groq_stt()
            print("[OK] Groq STT initialized")
            
            # Khởi tạo GUI nếu cần
            if self.gui_enabled:
                print("[GUI] Initializing GUI...")
                self._setup_gui()
                # Tạo overlay ngay từ đầu
                self._create_modern_overlay()
                print("[OK] GUI initialized")
            
            # Khởi tạo hotkey listener
            print("[HOTKEY] Initializing hotkey listener...")
            self._setup_hotkey()
            print("[OK] Hotkey listener initialized")

            # Khởi tạo text corrector
            print("[TEXT] Initializing text corrector...")
            self._setup_text_corrector()
            print("[OK] Text corrector initialized")

            print("[SUCCESS] Initialization complete!")
            self.logger.info("[OK] Khởi tạo thành công")
            
        except Exception as e:
            print(f"[ERROR] Initialization error: {e}")
            self.logger.error(f"[ERROR] Initialization error: {e}")
            raise
    
    def _init_groq_stt(self):
        """Khởi tạo Groq STT Service"""
        stt_cfg = self.config.get('stt', {})
        
        try:
            api_base = stt_cfg.get('api_base', 'https://api.groq.com/openai/v1')
            model = stt_cfg.get('model', 'whisper-large-v3')
            api_key_env = stt_cfg.get('api_key_env', 'GROQ_API_KEY')
            api_key = stt_cfg.get('api_key', None)
            api_keys = stt_cfg.get('api_keys', None)
            timeout = int(stt_cfg.get('timeout', 60))
            
            self.remote_stt = GroqSTTService(
                api_base=api_base, 
                model=model, 
                api_key_env=api_key_env,
                api_key=api_key,
                api_keys=api_keys,
                timeout=timeout
            )
            
            print(f"[OK] Using Groq Whisper STT: {model}")
            self.logger.info(f"[OK] Using Groq Whisper STT: {model}")
        except Exception as e:
            print(f"[ERROR] Groq STT init error: {e}")
            self.logger.error(f"[ERROR] Groq STT init error: {e}")
            raise
    
    def _setup_gui(self):
        """Thiết lập GUI - KHÔNG CẦN ROOT WINDOW"""
        try:
            print("[RENDER] Setting up GUI...")
            ctk.set_appearance_mode("light")
            ctk.set_default_color_theme("blue")
            
            # KHÔNG TẠO ROOT - Overlay sẽ tự tạo CTk window
            self.root = None
            
            self.logger.info("[OK] GUI setup (no root, overlay will create own window)")
        except Exception as e:
            print(f"[WARNING] Cannot setup GUI: {e}")
            self.logger.warning(f"[WARNING] Cannot setup GUI: {e}")
            self.gui_enabled = False
    
    def _setup_hotkey(self):
        """Setup hotkey với hold mode"""
        try:
            self.hotkey_manager.register(
                on_start=self._start_hold_recording,
                on_stop=self._stop_hold_recording,
                on_exit=self._on_exit_request
            )
            self.logger.info(f"[READY] Hotkey setup complete")
        except Exception as e:
            self.logger.error(f"[ERROR] Hotkey setup error: {e}")
            raise

    def _setup_text_corrector(self):
        """Thiết lập text corrector"""
        try:
            correction_config = self.config.get('text_correction', {})
            if correction_config.get('enabled', True):
                self.text_corrector = VietnameseTextCorrector(correction_config)
                self.logger.info("[OK] Text corrector đã được thiết lập")
            else:
                self.logger.info("[WARNING] Text correction bị tắt")
        except Exception as e:
            self.logger.error(f"[ERROR] Lỗi thiết lập text corrector: {e}")
            self.text_corrector = None
    
    def _start_hold_recording(self):
        """Callback khi BẮT ĐẦU giữ Ctrl+Alt"""
        if self.is_recording:
            return  # Already recording
        
        # Reset flags
        self.user_stopped_recording = False
        self.should_hide_gui = False
        
        # Show GUI
        if self.gui_enabled:
            try:
                self.gui_queue.put(("show_recording",))
            except Exception as e:
                print(f"[ERROR] Error showing GUI: {e}")
        
        # Start recording
        self._start_recording()
    
    def _stop_hold_recording(self):
        """Callback khi THẢ Ctrl+Alt"""
        print(f"[DEBUG] _stop_hold_recording called, is_recording={self.is_recording}")
        
        # Đánh dấu user đã thả phím (không hiển thị result GUI)
        self.user_stopped_recording = True
        
        # Set flag để main thread ẩn GUI (thread-safe)
        print("[DEBUG] Setting should_hide_gui flag...")
        self.should_hide_gui = True
        
        # Stop recording nếu đang record
        if self.is_recording:
            self._stop_recording()
        else:
            print("[DEBUG] Not recording, skip stop")
    
    def _on_exit_request(self):
        """Exit application"""
        print(f"[STOP] {self.exit_key.upper()} pressed - Exiting...")
        self.is_running = False
        threading.Thread(target=self.stop, daemon=True).start()

    def _process_gui_queue(self):
        """Xử lý GUI queue trong main thread"""
        try:
            while not self.gui_queue.empty():
                action, *args = self.gui_queue.get_nowait()
                print(f"[DEBUG] Processing GUI queue action: {action}")

                if action == "show_recording":
                    self._show_recording_gui_safe()
                elif action == "hide_gui":
                    print("[DEBUG] Queue action 'hide_gui' received")
                    self._hide_gui_safe()
                elif action == "show_processing":
                    self._show_processing_gui_safe()
                elif action == "show_result":
                    text = args[0] if args else ""
                    self._show_result_gui_safe(text)
                elif action == "show_error":
                    error = args[0] if args else ""
                    self._show_error_gui_safe(error)
                elif action == "update_wave":
                    level = args[0] if args else 0
                    self._update_wave_safe(level)

        except queue.Empty:
            pass
        except Exception as e:
            print(f"[ERROR] GUI queue error: {e}")

    def _show_recording_gui_safe(self):
        """Thread-safe version of show recording GUI"""
        if not self.gui_enabled:
            return
        try:
            if hasattr(self, 'overlay') and self.overlay:
                # Lấy quota info hiện tại
                quota_info = None
                if self.remote_stt:
                    try:
                        quota_info = self.remote_stt.get_quota_info()
                    except:
                        pass
                self.overlay.show_recording_safe(quota_info)
        except Exception as e:
            print(f"[ERROR] GUI error: {e}")

    def _hide_gui_safe(self):
        """Thread-safe version of hide GUI"""
        print("[DEBUG] _hide_gui_safe called")
        if hasattr(self, 'overlay') and self.overlay:
            try:
                print(f"[DEBUG] overlay exists, calling hide_immediately_safe()")
                self.overlay.hide_immediately_safe()
            except Exception as e:
                print(f"[ERROR] GUI hide error: {e}")
        else:
            print(f"[DEBUG] overlay not found: hasattr={hasattr(self, 'overlay')}, overlay={getattr(self, 'overlay', None)}")

    def _show_processing_gui_safe(self):
        """Thread-safe version of show processing GUI"""
        pass  # Implement if needed

    def _show_result_gui_safe(self, text: str):
        """Thread-safe version of show result GUI"""
        pass  # Implement if needed

    def _show_error_gui_safe(self, error: str):
        """Thread-safe version of show error GUI"""
        pass  # Implement if needed

    def _update_wave_safe(self, level: float):
        """Thread-safe version of update wave visualization - CỰC QUAN TRỌNG"""
        if hasattr(self, 'overlay') and self.overlay:
            try:
                # Kiểm tra overlay có sẵn sàng không
                if not hasattr(self.overlay, 'is_visible'):
                    return
                
                if not self.overlay.is_visible:
                    return
                
                # Cập nhật wave data - animation loop sẽ tự động vẽ lại
                self.overlay.update_wave_data(level)
            except Exception as e:
                # Chỉ in lỗi quan trọng
                if "wave" in str(e).lower():
                    print(f"[ERROR] Wave update error: {e}")
    
    def _start_recording(self):
        """Bắt đầu ghi âm"""
        if self.is_recording:
            return

        # Kiểm tra audio đã được khởi tạo chưa
        if self.audio is None:
            self.logger.error("[ERROR] Audio chưa được khởi tạo")
            print("[ERROR] Lỗi: Audio system chưa được khởi tạo!")
            print("[TIP] Please khởi động lại ứng dụng")
            return

        try:
            audio_config = self.config['audio']

            # Lấy input device index từ config (nếu có)
            input_device_index = audio_config.get('input_device_index', None)
            
            stream_params = {
                'format': pyaudio.paInt16,
                'channels': audio_config['channels'],
                'rate': audio_config['sample_rate'],
                'input': True,
                'frames_per_buffer': audio_config['chunk_size']
            }
            
            # Chỉ định device nếu có trong config
            if input_device_index is not None:
                stream_params['input_device_index'] = input_device_index
                print(f"[MIC] Using audio device index: {input_device_index}")
            else:
                print("[MIC] Using default audio device")
                print("[TIP] Để chọn thiết bị cụ thể, chạy: python check_audio_devices.py")

            self.stream = self.audio.open(**stream_params)
            print("[DEBUG] Audio stream created successfully")

            self.is_recording = True
            print(f"[DEBUG] is_recording = {self.is_recording}")
            
            self.audio_data = []
            print("[DEBUG] audio_data initialized")

            # Reset audio energy tracking
            self.total_audio_energy = 0
            self.audio_samples_count = 0
            print("[DEBUG] Audio energy tracking reset")

            # Bắt đầu thread ghi âm
            print("[DEBUG] Creating recording thread...")
            self.recording_thread = threading.Thread(target=self._recording_loop)
            self.recording_thread.daemon = True
            print("[DEBUG] Starting recording thread...")
            self.recording_thread.start()
            print("[DEBUG] Recording thread started")

            self.logger.info("[MIC] Bắt đầu ghi âm...")
            print("[MIC] RECORDING... (release hotkey to stop)")
            print("[TIP] Voice Activity Detection:", "BẬT" if audio_config.get('voice_activity_detection', False) else "TẮT")

        except Exception as e:
            self.logger.error(f"[ERROR] Lỗi bắt đầu ghi âm: {e}")
            print(f"[ERROR] Lỗi bắt đầu ghi âm: {e}")
            import traceback
            traceback.print_exc()
            self.is_recording = False
            # Ẩn GUI nếu có lỗi
            if self.gui_enabled:
                self._hide_gui()
    
    def _recording_loop(self):
        """Vòng lặp ghi âm"""
        audio_config = self.config['audio']
        silence_start = None
        recording_start = time.time()
        
        while self.is_recording:
            try:
                # Kiểm tra stream hợp lệ
                if not self.stream:
                    self.logger.error("[ERROR] Stream đã được đóng hoặc chưa khởi tạo")
                    break
                    
                data = self.stream.read(audio_config['chunk_size'], exception_on_overflow=False)
                self.audio_data.append(data)
                
                # Calculate audio level for visualization
                audio_array = np.frombuffer(data, dtype=np.int16)
                if len(audio_array) > 0:
                    # RMS (Root Mean Square) cho độ chính xác cao hơn
                    volume = np.sqrt(np.mean(audio_array.astype(np.float32)**2))
                    
                    # Normalize volume for visualization (0-1) - Tăng sensitivity
                    # Sử dụng scale factor thấp hơn để wave nhạy hơn
                    normalized_volume = min(volume / 500.0, 1.0)  # Giảm từ 1000 xuống 500
                    self.current_audio_level = normalized_volume

                    # Track total audio energy
                    self.total_audio_energy += volume
                    self.audio_samples_count += 1

                    # Send audio level to GUI - QUAN TRỌNG cho hiệu ứng wave
                    if self.gui_enabled:
                        try:
                            self.gui_queue.put(("update_wave", normalized_volume))
                            # Chỉ log khi có âm thanh đáng kể
                            if normalized_volume > 0.05:
                                print(f"[WAVE] Level: {normalized_volume:.3f}")
                        except Exception as e:
                            print(f"[ERROR] Queue error: {e}")
                else:
                    volume = 0
                    normalized_volume = 0
                    # Gửi level = 0 để wave về 0
                    if self.gui_enabled:
                        try:
                            self.gui_queue.put(("update_wave", 0.0))
                        except:
                            pass

                # Voice activity detection (chỉ khi bật)
                if audio_config.get('voice_activity_detection', False):
                    if volume > audio_config['silence_threshold']:
                        silence_start = None
                    else:
                        if silence_start is None:
                            silence_start = time.time()
                        elif time.time() - silence_start > audio_config['silence_duration']:
                            # Chỉ dừng nếu đã ghi đủ thời gian tối thiểu
                            if time.time() - recording_start >= audio_config.get('min_recording_time', 1.0):
                                self.logger.info("🔇 Phát hiện im lặng, dừng ghi âm")
                                break
                
                # Kiểm tra thời gian tối đa
                if time.time() - recording_start > audio_config['max_recording_time']:
                    self.logger.info("⏰ Đạt thời gian ghi âm tối đa")
                    break
                    
            except Exception as e:
                self.logger.error(f"[ERROR] Lỗi ghi âm: {e}")
                break
        
        # Tự động dừng
        if self.is_recording:
            self.is_recording = False
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            
            # Xử lý audio (chỉ khi chưa được xử lý)
            if self.audio_data:
                audio_bytes = b''.join(self.audio_data)
                self.audio_data = []  # Clear để tránh duplicate
                threading.Thread(target=self._process_audio, args=(audio_bytes,), daemon=True).start()
    
    def _stop_recording(self):
        """Stopping recording"""
        if not self.is_recording:
            return

        self.is_recording = False

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        self.logger.info("[STOP] Stopping recording")
        print("[STOP] Stopping recording - Processing...")

        # Xử lý audio (lấy và clear data ngay để tránh duplicate)
        if self.audio_data:
            audio_bytes = b''.join(self.audio_data)
            self.audio_data = []  # Clear ngay để tránh xử lý 2 lần!
            threading.Thread(target=self._process_audio, args=(audio_bytes,), daemon=True).start()
    
    def _process_audio(self, audio_data: bytes):
        """Xử lý audio và nhận dạng"""
        try:
            # Kiểm tra mức độ âm thanh trung bình
            if self.audio_samples_count > 0:
                avg_audio_energy = self.total_audio_energy / self.audio_samples_count
                min_energy_threshold = 50  # Ngưỡng âm thanh tối thiểu

                if avg_audio_energy < min_energy_threshold:
                    self.logger.info("🔇 Âm thanh quá nhỏ, bỏ qua nhận dạng")
                    print("🔇 Không phát hiện giọng nói rõ ràng")
                    # Ensure GUI is hidden
                    if self.gui_enabled:
                        try:
                            self.gui_queue.put(("hide_gui",))
                        except:
                            pass
                    return

                self.logger.info(f"🎵 Mức âm thanh trung bình: {avg_audio_energy:.1f}")

            self.logger.info("[DEBUG] Đang nhận dạng giọng nói...")
            print("[DEBUG] Đang nhận dạng giọng nói...")

            # Tạo file tạm
            temp_fd, temp_path = tempfile.mkstemp(suffix='.wav')
            
            try:
                # Chuyển đổi và xử lý audio data
                audio_array = np.frombuffer(audio_data, dtype=np.int16)

                # Kiểm tra độ dài audio tối thiểu
                duration_seconds = len(audio_array) / self.config['audio']['sample_rate']
                min_duration = self.config['audio'].get('min_recording_time', 1.0)  # Tối thiểu 1.0 seconds

                if duration_seconds < min_duration:
                    self.logger.info(f"🔇 Audio quá ngắn ({duration_seconds:.2f}s < {min_duration}s), bỏ qua nhận dạng")
                    print(f"🔇 Record quá ngắn ({duration_seconds:.2f}s) - cần ít nhất {min_duration}s")
                    print("[TIP] Thử nói lâu hơn để có kết quả chính xác hơn")
                    # Ensure GUI is hidden
                    if self.gui_enabled:
                        try:
                            self.gui_queue.put(("hide_gui",))
                        except:
                            pass
                    return

                # Cải thiện chất lượng audio
                audio_array = self._enhance_audio(audio_array)

                with wave.open(temp_path, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(self.config['audio']['sample_rate'])
                    wav_file.writeframes(audio_array.tobytes())
                
                # Nhận dạng bằng Groq STT
                try:
                    stt_config = self.config.get('stt', {})
                    language = stt_config.get('language', 'vi')
                    print("[NET] Gọi Groq STT...")
                    recognized_text = self.remote_stt.transcribe(temp_path, language=language)
                    
                    # Cập nhật quota info lên GUI
                    if self.gui_enabled and self.overlay:
                        try:
                            quota_info = self.remote_stt.get_quota_info()
                            self.root.after(0, lambda: self.overlay.update_quota_info(quota_info))
                        except Exception as e:
                            pass
                            
                except Exception as e:
                    self.logger.error(f"[ERROR] Lỗi Groq STT: {e}")
                    print(f"[ERROR] Lỗi Groq STT: {e}")
                    # Ensure GUI is hidden
                    if self.gui_enabled:
                        try:
                            self.gui_queue.put(("hide_gui",))
                        except:
                            pass
                    return

                # Post-processing cho tiếng Việt
                recognized_text = self._post_process_vietnamese_text(recognized_text, language)

                if recognized_text and self._is_meaningful_text(recognized_text):
                    self.logger.info(f"[OK] Nhận dạng thành công: '{recognized_text}'")
                    print(f"[OK] Result: '{recognized_text}'")
                    print("[TEXT] Pasting text...")

                    if self.gui_enabled and self.root:
                        try:
                            self.root.after(0, lambda: self._show_result_gui(recognized_text))
                        except:
                            pass

                    self._paste_text(recognized_text)
                else:
                    self.logger.warning("[WARNING] Cannot recognize text")
                    print("[WARNING] Cannot recognize text")
                    if self.gui_enabled and self.root:
                        try:
                            self.root.after(0, lambda: self._show_error_gui("Cannot recognize text"))
                        except:
                            pass
                
            finally:
                # Xóa file tạm
                try:
                    os.close(temp_fd)
                    os.unlink(temp_path)
                except:
                    pass
                    
        except Exception as e:
            error_msg = f"Lỗi nhận dạng: {e}"
            self.logger.error(f"[ERROR] {error_msg}")
            print(f"[ERROR] {error_msg}")
            
            if self.gui_enabled and self.root:
                self.root.after(0, lambda: self._show_error_gui(error_msg))
        
        # Không cần ẩn GUI ở đây vì đã ẩn khi thả hotkey

    def _enhance_audio(self, audio_array: np.ndarray) -> np.ndarray:
        """Cải thiện chất lượng audio cho nhận dạng tốt hơn với các kỹ thuật nâng cao"""
        try:
            audio_config = self.config['audio'].get('audio_enhancement', {})
            if not audio_config.get('enabled', True):
                return audio_array.astype(np.int16)

            # Chuyển đổi sang float32 để xử lý chính xác hơn
            if np.max(np.abs(audio_array)) == 0:
                return audio_array.astype(np.int16)
                
            audio_float = audio_array.astype(np.float32)
            
            # 1. Loại bỏ DC offset (dịch chuyển DC)
            if audio_config.get('reduce_noise', True):
                audio_float = audio_float - np.mean(audio_float)
            
            # 2. Chuẩn hóa âm lượng ban đầu
            if audio_config.get('normalize_volume', True):
                max_val = np.max(np.abs(audio_float))
                if max_val > 0:
                    audio_float = audio_float / max_val * 0.85  # Giữ lại headroom
            
            # 3. Lọc thông cao để loại bỏ tiếng ồn tần số thấp
            if audio_config.get('apply_filter', True) and len(audio_float) > 2:
                # High-pass filter đơn giản (RC filter)
                alpha = 0.97  # Cut-off frequency khoảng 50Hz ở 16kHz
                filtered = np.zeros_like(audio_float)
                filtered[0] = audio_float[0]
                for i in range(1, len(audio_float)):
                    filtered[i] = alpha * (filtered[i-1] + audio_float[i] - audio_float[i-1])
                audio_float = filtered
            
            # 4. Giảm tiếng ồn thông minh (Spectral Subtraction đơn giản)
            if audio_config.get('reduce_noise', True) and len(audio_float) > 512:
                # Ước lượng tiếng ồn từ 10% đầu của signal
                noise_sample_length = min(len(audio_float) // 10, 1600)  # 0.1s ở 16kHz
                noise_estimate = np.std(audio_float[:noise_sample_length])
                
                # Chỉ áp dụng nếu có tiếng ồn đáng kể
                if noise_estimate > 0:
                    # Soft thresholding
                    threshold = noise_estimate * 2.0
                    audio_float = np.where(
                        np.abs(audio_float) > threshold,
                        audio_float,
                        audio_float * 0.3  # Giảm tiếng ồn xuống 30%
                    )
            
            # 5. Tự động điều chỉnh khuếch đại thông minh
            if audio_config.get('normalize_volume', True):
                # Tính RMS (Root Mean Square) cho mức âm thanh trung bình
                rms = np.sqrt(np.mean(audio_float**2))
                if rms > 0:
                    # Mục tiêu RMS tối ưu cho speech recognition
                    target_rms = 0.25
                    gain = target_rms / rms
                    
                    # Giới hạn gain để tránh clip và nhiễu quá mức
                    gain = min(gain, 4.0)  # Tối đa 4x
                    gain = max(gain, 0.1)  # Tối thiểu 0.1x
                    
                    audio_float = audio_float * gain
            
            # 6. Nén động (Dynamic Range Compression) để cân bằng âm thanh
            if audio_config.get('enhance_speech', True):
                # Soft limiter để giảm dynamic range quá lớn
                threshold = 0.8
                ratio = 0.5  # Compression ratio
                
                abs_audio = np.abs(audio_float)
                over_threshold = abs_audio > threshold
                
                if np.any(over_threshold):
                    # Áp dụng compression cho các sample vượt ngưỡng
                    compressed = threshold + (abs_audio - threshold) * ratio
                    audio_float = np.where(
                        over_threshold,
                        np.sign(audio_float) * compressed,
                        audio_float
                    )
            
            # 7. Chuẩn hóa cuối cùng và chuyển về int16
            # Đảm bảo không bị clip
            max_val = np.max(np.abs(audio_float))
            if max_val > 0.95:
                audio_float = audio_float / max_val * 0.95
            
            # Chuyển về int16 với giới hạn chính xác
            audio_int16 = np.clip(audio_float * 32767, -32768, 32767).astype(np.int16)
            
            # Kiểm tra chất lượng kết quả
            final_rms = np.sqrt(np.mean((audio_int16.astype(np.float32) / 32767)**2))
            self.logger.debug(f"🎧 Audio enhancement: RMS = {final_rms:.3f}, Max = {np.max(np.abs(audio_int16))}")
            
            return audio_int16

        except Exception as e:
            self.logger.warning(f"Lỗi xử lý audio nâng cao: {e}")
            # Fallback về normalize đơn giản
            try:
                if np.max(np.abs(audio_array)) > 0:
                    normalized = audio_array.astype(np.float32)
                    normalized = normalized / np.max(np.abs(normalized)) * 0.8
                    return np.clip(normalized * 32767, -32768, 32767).astype(np.int16)
            except:
                pass
            return audio_array.astype(np.int16)

    def _post_process_vietnamese_text(self, text: str, language: str = "vi") -> str:
        """Post-processing cho văn bản tiếng Việt với AI text correction"""
        if not text:
            return text

        try:
            # 1. AI Text Correction (nếu được bật)
            if self.text_corrector and language == "vi":
                text = self.text_corrector.correct_text(text, language)

            # 2. Legacy corrections (backup cho các trường hợp đặc biệt)
            text = self._apply_legacy_corrections(text)

            return text

        except Exception as e:
            self.logger.warning(f"Lỗi post-processing: {e}")
            return text

    def _apply_legacy_corrections(self, text: str) -> str:
        """Áp dụng corrections cũ làm backup"""
        try:
            # Loại bỏ khoảng trắng thừa
            text = " ".join(text.split())

            # Một số corrections đặc biệt không có trong dictionary
            special_corrections = {
                "xin kéo": "xin chào",
                "xin gào": "xin chào",
                "xin gao": "xin chào",
                "xin kao": "xin chào",
                "sin chào": "xin chào",
            }

            # Pattern-based corrections cho lỗi nhận dạng phổ biến
            import re

            # Sửa "quê không" thành "khỏe không" trong ngữ cảnh hỏi thăm
            text = re.sub(r'\b(bạn|ban)\s+(quê|que)\s+(không|khong|ko)\b',
                         r'\1 khỏe không', text, flags=re.IGNORECASE)

            # Sửa "xin chào bạn quê không" thành "xin chào bạn khỏe không"
            text = re.sub(r'\b(xin\s+chào|chào)\s+(bạn|ban)\s+(quê|que)\s+(không|khong|ko)\b',
                         r'\1 \2 khỏe không', text, flags=re.IGNORECASE)

            # Áp dụng special corrections
            text_lower = text.lower()
            for wrong, correct in special_corrections.items():
                if wrong in text_lower:
                    # Giữ nguyên case của từ đầu tiên
                    if text and text[0].isupper():
                        correct = correct.capitalize()
                    text = text_lower.replace(wrong, correct)
                    break

            return text

        except Exception as e:
            self.logger.warning(f"Lỗi legacy corrections: {e}")
            return text

    def _is_meaningful_text(self, text: str) -> bool:
        """Kiểm tra văn bản có ý nghĩa hay không"""
        if not text or len(text.strip()) < 2:
            return False

        text = text.lower().strip()

        # Loại bỏ các văn bản không có ý nghĩa
        meaningless_patterns = [
            # Các từ lặp lại
            r'(.)\1{4,}',  # Ký tự lặp lại 5 lần trở lên
            r'\b(\w+)\s+\1\s+\1\s+\1',  # Từ lặp lại 4 lần

            # Các cụm từ vô nghĩa
            r'^(uh|um|ah|eh|mm|hmm|hm)+\.?$',
            r'^(hello\?|hi\?|hey\?)\.?$',
            r'^(cảm ơn .*){3,}',  # "cảm ơn" lặp lại nhiều lần
            r'^(kênh .*){5,}',    # "kênh" lặp lại nhiều lần

            # Chỉ có dấu câu
            r'^[^\w\s]*$',

            # Văn bản quá ngắn và vô nghĩa
            r'^[a-z]\.?$',  # Chỉ một chữ cái
        ]

        import re
        for pattern in meaningless_patterns:
            if re.search(pattern, text):
                self.logger.info(f"🔇 Văn bản vô nghĩa bị loại bỏ: '{text}'")
                return False

        # Kiểm tra tỷ lệ từ lặp lại
        words = text.split()
        if len(words) > 3:
            unique_words = set(words)
            repetition_ratio = len(words) / len(unique_words)
            if repetition_ratio > 3:  # Quá nhiều từ lặp lại
                self.logger.info(f"🔇 Quá nhiều từ lặp lại: '{text}'")
                return False

        return True
    
    def _normalize_duplicate_text(self, text: str) -> str:
        """Chuẩn hoá nếu văn bản vô tình bị lặp 2 lần liên tiếp"""
        try:
            t = text.strip()
            # Trường hợp độ dài gấp đôi và hai nửa giống nhau (bỏ khoảng trắng biên)
            if len(t) % 2 == 0:
                half = len(t) // 2
                first = t[:half].strip()
                second = t[half:].strip()
                if first and first == second:
                    return first

            # So sánh theo token (bỏ khoảng trắng)
            tokens = t.split()
            if len(tokens) % 2 == 0 and tokens:
                mid = len(tokens) // 2
                if tokens[:mid] == tokens[mid:]:
                    return " ".join(tokens[:mid])
        except Exception:
            pass
        return text

    def _paste_text(self, text: str):
        """Dán văn bản to ứng dụng đích"""
        try:
            # Debounce tránh dán trùng trong thời gian ngắn
            now = time.time()
            candidate = text.strip()
            if candidate and candidate == self._last_paste_text and (now - self._last_paste_at) < 1.0:
                self.logger.info("⏩ Bỏ qua dán trùng (debounce)")
                return

            # Chuẩn hoá chống lặp (nếu có)
            text = self._normalize_duplicate_text(text)

            # Lưu clipboard cũ
            try:
                old_clipboard = pyperclip.paste()
            except:
                old_clipboard = ""
            
            # Copy văn bản mới
            pyperclip.copy(text)
            time.sleep(0.05)  # Giảm từ 0.2 → 0.05
            
            # Thử paste
            method = self.config['text_input']['method']
            
            if method == 'paste':
                # Thử Ctrl+V
                import keyboard as kb
                kb.send('ctrl+v')
                time.sleep(0.1)  # Giảm từ 0.3 → 0.1
                self.logger.info("[OK] Đã dán văn bản bằng Ctrl+V")
            else:
                # Typing từng ký tự
                import keyboard as kb
                kb.write(text)
                time.sleep(0.05)  # Giảm từ 0.1 → 0.05
                self.logger.info("[OK] Đã gõ văn bản")
            
            print("[OK] Text pasted successfully!")
            print("[READY] Ready for next recording...")
            
            # Lưu trạng thái paste gần nhất
            self._last_paste_text = candidate
            self._last_paste_at = now
            
            # Khôi phục clipboard
            try:
                time.sleep(0.05)  # Giảm từ 0.1 → 0.05
                pyperclip.copy(old_clipboard)
            except:
                pass
                
        except Exception as e:
            self.logger.error(f"[ERROR] Text paste error: {e}")
            print(f"[ERROR] Text paste error: {e}")
    
    # GUI Methods - Modern Overlay System
    def _show_recording_gui(self):
        """Hiển thị GUI ghi âm hiện đại (deprecated - use queue)"""
        # This method is deprecated, use GUI queue instead
        pass

    def _show_processing_gui(self):
        """Hiển thị GUI xử lý"""
        if self.gui_enabled and hasattr(self, 'overlay') and self.overlay:
            try:
                self.overlay.show_processing()
            except:
                pass

    def _show_result_gui(self, text: str):
        """Hiển thị GUI kết quả"""
        # Không hiển thị nếu user đã thả hotkey
        if self.user_stopped_recording:
            print("[DEBUG] User stopped recording, skip showing result GUI")
            return
            
        if self.gui_enabled and hasattr(self, 'overlay') and self.overlay:
            try:
                self.overlay.show_result(text)
            except:
                pass

    def _show_error_gui(self, error: str):
        """Hiển thị GUI lỗi"""
        # Không hiển thị nếu user đã thả hotkey
        if self.user_stopped_recording:
            print("[DEBUG] User stopped recording, skip showing error GUI")
            return
            
        if self.gui_enabled and hasattr(self, 'overlay') and self.overlay:
            try:
                self.overlay.show_error(error)
            except:
                pass

    def _hide_gui(self):
        """Ẩn GUI ngay lập tức (deprecated - use queue)"""
        # This method is deprecated, use GUI queue instead
        pass

    def _create_modern_overlay(self):
        """Tạo overlay hiện đại - CHỈ TẠO 1 LẦN, KHÔNG CẦN ROOT"""
        try:
            # Đảm bảo chỉ tạo 1 overlay duy nhất
            if self.overlay is not None:
                print("[WARNING] Overlay already exists, skip creating new one")
                return
                
            print("[RENDER] Creating standalone overlay window (no parent)...")
            self.overlay = ModernVoiceOverlay(None, self.config['gui'])
            
            # Set root to overlay window để dùng cho update
            self.root = self.overlay.window
            
            self.logger.info("[OK] Standalone overlay created")
            print("[OK] 1 standalone overlay window created")
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to create overlay: {e}")
            print(f"[ERROR] Failed to create overlay: {e}")
            self.overlay = None
            self.gui_enabled = False
    
    def start(self):
        """Bắt đầu ứng dụng"""
        try:
            self.is_running = True
            
            # Check if hotkey registered
            if not self.hotkey_manager.is_registered:
                self.logger.error("[ERROR] Hotkey not registered")
                print("[ERROR] Error: Hotkey not registered!")
                return
            
            print(f"[READY] Application ready!")
            print(f"[HOTKEY] HOLD {self.record_key.upper()} to record, RELEASE to stop")
            print(f"[STOP] Press {self.exit_key.upper()} to exit")
            print()
            print("[TIP] USAGE GUIDE:")
            print("   1. Open Notepad and click on it")
            print(f"   2. HOLD {self.record_key.upper()} and speak")
            print("   3. Speak clearly to microphone (Vietnamese)")
            print(f"   4. RELEASE {self.record_key.upper()} to stop and transcribe")
            print("   5. Text will be pasted automatically")
            print()
            print("[READY] TIPS:")
            print("   - Speak clearly, moderate speed")
            print("   - Avoid background noise")
            print("   - Hold at least 2-3 seconds")
            print()
            
            # Vòng lặp chính
            while self.is_running:
                try:
                    # Xử lý GUI queue trước
                    if self.gui_enabled:
                        self._process_gui_queue()
                    
                    # Kiểm tra flag để ẩn GUI
                    if self.should_hide_gui:
                        print("[DEBUG] should_hide_gui flag detected, hiding GUI now...")
                        self.should_hide_gui = False
                        if self.gui_enabled and hasattr(self, 'overlay') and self.overlay:
                            try:
                                self.overlay.is_visible = False
                                self.overlay._stop_animation()
                                if self.overlay.window:
                                    self.overlay.window.withdraw()
                                    print("[OK] GUI hidden from main thread")
                            except Exception as e:
                                print(f"[ERROR] Error hiding GUI from main thread: {e}")

                    # Cập nhật GUI - CHỈ update overlay, KHÔNG update root
                    if self.gui_enabled and self.overlay and self.overlay.window:
                        try:
                            self.overlay.window.update()
                        except:
                            pass
                    elif self.gui_enabled and self.root:
                        # Fallback: dùng update_idletasks thay vì update để tránh show root
                        try:
                            self.root.update_idletasks()
                        except:
                            pass
                    time.sleep(0.01)
                except Exception as loop_error:
                    # Log exception để debug
                    print(f"[ERROR] Main loop error: {loop_error}")
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            print("\n[HOTKEY] Received stop signal")
        except Exception as e:
            self.logger.error(f"[ERROR] Lỗi vòng lặp chính: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Dừng ứng dụng"""
        print("[HALT] Stopping application...")
        
        self.is_running = False
        
        # Stopping recording
        if self.is_recording:
            self.is_recording = False
        
        # Unhook hotkeys
        if self.hotkey_manager:
            self.hotkey_manager.unregister()
        
        # Dọn dẹp audio
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.audio:
            self.audio.terminate()
        
        # Dọn dẹp GUI
        if hasattr(self, 'overlay') and self.overlay:
            try:
                self.overlay.cleanup()
            except:
                pass

        if self.gui_enabled and self.root:
            try:
                self.root.destroy()
            except:
                pass
        
        print("[OK] Application stopped")
