"""
Groq STT Service - Speech to text using Groq Whisper API
"""
import os
from typing import Set

try:
    import requests
except Exception:
    requests = None


class GroqSTTService:
    """Dịch vụ STT dùng Groq Whisper (OpenAI-compatible API) với hỗ trợ nhiều API keys"""

    def __init__(self, api_base: str, model: str = "whisper-large-v3", api_key_env: str = "GROQ_API_KEY", 
                 api_key: str = None, api_keys: list = None, timeout: int = 60):
        self.api_base = api_base.rstrip('/')
        self.model = model
        self.api_key_env = api_key_env
        self.timeout = timeout
        
        # Quota tracking
        self.current_quota_info = {
            'remaining': None,  # Sẽ được update từ API response
            'limit': None,
            'reset': None,
            'key_index': 0
        }
        
        # Fake quota để test UI (sẽ bị override bởi real data nếu API trả về)
        self.use_fake_quota = False  # TEMPORARY: Enable để test UI, sẽ bị replace bởi real data
        
        # Xây dựng array API keys
        self.api_keys = []
        
        # 1. Add key từ biến môi trường (nếu có)
        env_key = os.environ.get(api_key_env)
        if env_key:
            self.api_keys.append(env_key)
        
        # 2. Add key đơn lẻ từ config (nếu có)
        if api_key:
            if api_key not in self.api_keys:
                self.api_keys.append(api_key)
        
        # 3. Add array keys từ config (nếu có)
        if api_keys and isinstance(api_keys, list):
            for key in api_keys:
                if key and key not in self.api_keys:
                    self.api_keys.append(key)
        
        # Kiểm tra có ít nhất 1 key
        if not self.api_keys:
            raise ValueError(
                f"Missing API key! Please:\n"
                f"  1. Set environment variable {api_key_env}, OR\n"
                f"  2. Add 'api_key' to config.json > stt, OR\n"
                f"  3. Add 'api_keys' (array) to config.json > stt\n"
                f"     Example: \"api_keys\": [\"gsk_...\", \"gsk_...\"]"
            )
        
        # Index của key hiện tại
        self.current_key_index = 0
        
        print(f"[OK] Loaded {len(self.api_keys)} API key(s)")
        if len(self.api_keys) > 1:
            print(f"   -> Supports auto-rotation when quota exceeded")
    
    def get_quota_info(self) -> dict:
        """Lấy thông tin quota hiện tại"""
        # Nếu dùng fake quota cho test
        if self.use_fake_quota and self.current_quota_info.get('remaining') is None:
            return {
                'remaining': 480,  # Fake data
                'limit': 500,
                'reset': None,
                'key_index': self.current_key_index + 1,
                'total_keys': len(self.api_keys)
            }
        
        return {
            'remaining': self.current_quota_info.get('remaining'),
            'limit': self.current_quota_info.get('limit'),
            'reset': self.current_quota_info.get('reset'),
            'key_index': self.current_key_index + 1,
            'total_keys': len(self.api_keys)
        }
    
    def _update_quota_from_headers(self, headers: dict):
        """Cập nhật thông tin quota từ response headers"""
        try:
            # Debug: In ra tất cả headers để xem
            print(f"[DEBUG] Response headers: {dict(headers)}")
            
            # Groq API có thể dùng các tên headers khác nhau
            # Thử các biến thể có thể
            header_variants = [
                'x-ratelimit-remaining-requests',
                'x-ratelimit-remaining',
                'ratelimit-remaining',
                'x-ratelimit-remaining-tokens'
            ]
            
            for variant in header_variants:
                if variant in headers:
                    self.current_quota_info['remaining'] = int(headers.get(variant, 0))
                    print(f"[DEBUG] Found remaining in header: {variant} = {self.current_quota_info['remaining']}")
                    break
            
            limit_variants = [
                'x-ratelimit-limit-requests',
                'x-ratelimit-limit',
                'ratelimit-limit',
                'x-ratelimit-limit-tokens'
            ]
            
            for variant in limit_variants:
                if variant in headers:
                    self.current_quota_info['limit'] = int(headers.get(variant, 0))
                    print(f"[DEBUG] Found limit in header: {variant} = {self.current_quota_info['limit']}")
                    break
            
            if 'x-ratelimit-reset-requests' in headers:
                self.current_quota_info['reset'] = headers.get('x-ratelimit-reset-requests')
            
            self.current_quota_info['key_index'] = self.current_key_index
            
            # Nếu không tìm thấy quota info, log warning
            if self.current_quota_info['remaining'] is None:
                print(f"[WARNING] Không tìm thấy quota info trong response headers")
                print(f"[INFO] Headers available: {list(headers.keys())}")
            
        except Exception as e:
            print(f"[ERROR] Lỗi parse quota headers: {e}")
            pass

    def _get_current_key(self) -> str:
        """Lấy API key hiện tại"""
        return self.api_keys[self.current_key_index]
    
    def _rotate_key(self, tried_indices: set) -> bool:
        """
        Switching to API key tiếp theo chưa thử.
        Args:
            tried_indices: Set các index đã thử
        Returns:
            True nếu còn key khác, False nếu đã thử hết
        """
        if len(self.api_keys) <= 1:
            return False  # Chỉ có 1 key, không thể rotate
        
        # Thử tìm key tiếp theo chưa được thử
        for _ in range(len(self.api_keys)):
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            
            # Nếu tìm thấy key chưa thử
            if self.current_key_index not in tried_indices:
                key_preview = self._get_current_key()[:20] + "..."
                print(f"[ROTATE] Switching to API key #{self.current_key_index + 1}/{len(self.api_keys)} ({key_preview})")
                return True
        
        # Tried all tất cả keys
        print(f"[WARNING] Tried all {len(self.api_keys)} API keys")
        return False

    def transcribe(self, wav_path: str, language: str = "vi") -> str:
        if requests is None:
            raise ImportError("Thiếu thư viện 'requests'. Please cài: pip install requests")

        url = f"{self.api_base}/audio/transcriptions"
        data = {"model": self.model, "language": language, "response_format": "json"}

        # Track các key đã thử để không thử lại
        tried_indices = set()
        last_error = None
        
        while len(tried_indices) < len(self.api_keys):
            try:
                # Đánh dấu key hiện tại đã được thử
                tried_indices.add(self.current_key_index)
                
                current_key = self._get_current_key()
                key_preview = current_key[:20] + "..."
                
                if len(tried_indices) == 1:
                    print(f"[NET] Calling Groq STT with API key #{self.current_key_index + 1}/{len(self.api_keys)}...")
                
                headers = {"Authorization": f"Bearer {current_key}"}
                
                with open(wav_path, "rb") as f:
                    files = {"file": ("audio.wav", f, "audio/wav")}
                    resp = requests.post(url, headers=headers, data=data, files=files, timeout=self.timeout)
                
                # Kiểm tra lỗi quota (429 - Too Many Requests)
                if resp.status_code == 429:
                    print(f"[WARNING] API key #{self.current_key_index + 1} out of quota (429)")
                    
                    # Thử rotate sang key khác chưa thử
                    if self._rotate_key(tried_indices):
                        continue  # Thử lại với key mới
                    else:
                        raise Exception(
                            f"Tất cả {len(self.api_keys)} API keys đều hết quota!\n"
                            f"[TIP] Please đợi hoặc thêm thêm API keys to config.json"
                        )
                
                # Kiểm tra lỗi 401 trước raise_for_status
                if resp.status_code == 401:
                    print(f"[WARNING] API key #{self.current_key_index + 1} invalid (401)")
                    
                    # Thử rotate sang key khác chưa thử
                    if self._rotate_key(tried_indices):
                        continue
                    else:
                        raise Exception(
                            f"Tất cả {len(self.api_keys)} API keys đều invalid!\n"
                            f"[TIP] Please kiểm tra lại keys tại: https://console.groq.com/keys"
                        )
                
                # Kiểm tra lỗi khác
                resp.raise_for_status()
                
                # Cập nhật quota info từ headers
                self._update_quota_from_headers(resp.headers)
                
                # Parse response
                payload = resp.json()
                text = payload.get("text")
                if not text:
                    raise ValueError("Phản hồi Groq không có trường 'text'")
                
                # Thành công - Log quota info
                quota_info = self.get_quota_info()
                if len(tried_indices) > 1:
                    print(f"[OK] Recognition successful with API key #{self.current_key_index + 1} (đã thử {len(tried_indices)} keys)")
                
                if quota_info['remaining'] is not None:
                    print(f"[STAT] Quota remaining: {quota_info['remaining']}/{quota_info['limit']} requests")
                
                return text
                
            except requests.exceptions.RequestException as e:
                last_error = e
                
                # Network/timeout errors - thử key khác
                if len(tried_indices) < len(self.api_keys):
                    print(f"[WARNING] Connection error với API key #{self.current_key_index + 1}: {str(e)[:50]}")
                    if self._rotate_key(tried_indices):
                        continue
                
                # Tried all keys hoặc lỗi nghiêm trọng
                raise Exception(f"Connection error Groq API: {e}")
                
            except Exception as e:
                # Lỗi khác (parse JSON, file không tồn tại...) - không retry
                raise
        
        # Nếu đã thử hết mà vẫn lỗi
        if last_error:
            raise last_error
        
        raise Exception(f"Không thể nhận dạng giọng nói sau khi thử {len(self.api_keys)} API keys")
