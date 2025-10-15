"""
Modern Voice Overlay - HOÀN TOÀN MỚI - CHỈ 1 WINDOW
"""
import customtkinter as ctk
import tkinter as tk
import threading
import time
import math


class ModernVoiceOverlay:
    """GUI overlay hiện đại - ĐƠN GIẢN, CHỈ 1 WINDOW"""
    
    def __init__(self, parent, config: dict):
        """
        Args:
            parent: None (không dùng)
            config: Cấu hình GUI
        """
        self.config = config
        self.is_visible = False
        
        # Animation states
        self.animation_running = False
        self.wave_phase = 0
        
        # Wave data - Tăng lên 120 bars cho mịn hơn
        self.wave_data = [0] * 120
        self.wave_smoothing = 0.2  # Giảm để phản ứng nhanh hơn
        self.current_mic_level = 0
        
        # Wave bars
        self.wave_bars = []
        self.wave_bars_created = False
        
        print("[RENDER] Creating NEW simple overlay...")
        self._create_window()
    
    def _create_window(self):
        """Tạo 1 window duy nhất"""
        try:
            # TẠO 1 CTk WINDOW DUY NHẤT
            self.window = ctk.CTk()
            self.window.title("[MIC] Voice to Text")
            
            # Cấu hình window
            width = self.config.get('window_width', 900)
            height = self.config.get('window_height', 700)
            
            # Vị trí: dưới cùng màn hình, center ngang
            # Vị trí: dưới cùng (sát taskbar), center ngang
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            x = (screen_width - width) // 2  # Center ngang chính xác
            y = screen_height - height  
            
            self.window.geometry(f"{width}x{height}+{x}+{y}")
            self.window.attributes("-topmost", True)
            self.window.resizable(False, False)
            self.window.overrideredirect(True)  # Loại bỏ title bar để bo tròn góc
            
            # Làm background window trong suốt
            try:
                # Set theme appearance (cần cho CustomTkinter)
                ctk.set_appearance_mode("dark")
                
                # Windows specific - transparent background
                self.window.wm_attributes('-transparentcolor', '#000001')
                self.window.configure(bg='#000001')
                
                # Đảm bảo window CTk cũng trong suốt
                self.window._apply_appearance_mode(ctk.get_appearance_mode())
            except Exception as e:
                print(f"[WARN] Transparency setup: {e}")
            
            # Tạo UI
            self._create_ui()
            
            # Protocol để handle close button
            self.window.protocol("WM_DELETE_WINDOW", self._on_close)
            
            # Ẩn ban đầu
            self.window.withdraw()
            
            print("[OK] 1 window created successfully")
            
        except Exception as e:
            import traceback
            print(f"[ERROR] Failed to create window: {e}")
            print(f"[ERROR] Full traceback:")
            print(traceback.format_exc())
            self.window = None
    
    def _create_ui(self):
        """Tạo giao diện đơn giản"""
        # Main frame với nền trong suốt
        self.main_frame = ctk.CTkFrame(
            self.window,
            corner_radius=20,
            fg_color="#000001",  # Trong suốt (match với transparent color)
            border_width=0,
            bg_color="#000001"  # Background color trong suốt
        )
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Close button (góc trên cùng bên phải)
        close_btn = ctk.CTkButton(
            self.main_frame,
            text="✕",
            width=28,
            height=28,
            fg_color="#ef4444",
            hover_color="#dc2626",
            corner_radius=14,
            command=self._on_close,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        close_btn.place(x=308, y=5)  # Góc trên phải (điều chỉnh theo width mới)
        
        # Micro với vòng tròn màu xanh lá
        self.mic_frame = ctk.CTkFrame(  # Lưu làm instance variable
            self.main_frame,
            width=50,
            height=50,
            fg_color="#0fb77f",  # Màu xanh lá
            corner_radius=25  # Bo tròn hoàn toàn (radius = width/2)
        )
        self.mic_frame.pack(side="bottom", pady=(0, 12))
        self.mic_frame.pack_propagate(False)
        
        mic_label = ctk.CTkLabel(
            self.mic_frame,
            text="🎤", 
            font=ctk.CTkFont(size=28),
            fg_color="transparent",
            text_color="#000000"  # Màu đen
        )
        mic_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Wave frame với nền xanh lá
        self.wave_frame = ctk.CTkFrame(
            self.main_frame,
            height=70,
            fg_color="#0fb77f",
            corner_radius=12
        )
        self.wave_frame.pack(side="bottom", fill="x", padx=15, pady=(0, 8))
        self.wave_frame.pack_propagate(False)
        
        # Canvas với nền xanh lá
        self.wave_canvas = tk.Canvas(
            self.wave_frame,  # Sử dụng self.wave_frame
            bg="#0fb77f",  # Xanh lá
            highlightthickness=0,
            bd=0
        )
        self.wave_canvas.pack(expand=True, fill="both", padx=8, pady=8)
        
        # Quota/progress ẩn (giữ lại để code không lỗi)
        info_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        # Không pack() = không hiển thị
        
        self.quota_label = ctk.CTkLabel(
            info_frame,
            text="🔑 API Key #1/5",
            font=ctk.CTkFont(size=10),
            text_color="#9ca3af"
        )
        
        self.progress = ctk.CTkProgressBar(
            info_frame,
            width=250,
            height=6,
            corner_radius=3,
            fg_color="#e5e7eb",
            progress_color="#3b82f6"
        )
        self.progress.set(0)
        
        # Status label (giữ lại để code không lỗi, nhưng không hiển thị)
        self.status_label = ctk.CTkLabel(
            info_frame,
            text="",
            font=ctk.CTkFont(size=1),
            text_color="white"  # Màu trắng blend với background
        )
        # Không pack() = không hiển thị
        
        print("[OK] UI created")
    
    def _on_close(self):
        """Đóng window và thoát app - Được gọi từ title bar X button"""
        try:
            print("[EXIT] Closing app via title bar...")
            self.cleanup()
            import os
            os._exit(0)  # Force exit
        except Exception as e:
            print(f"[ERROR] Exit error: {e}")
            import os
            os._exit(1)
    
    def show_recording_safe(self, quota_info=None):
        """Hiển thị window khi recording với animation"""
        print("[DEBUG] show_recording_safe called")
        try:
            if not self.window:
                print("[ERROR] window is None!")
                return
            
            print("[DEBUG] Setting visible and resetting wave data...")
            self.is_visible = True
            
            # Reset wave data
            self.wave_data = [0] * 120
            
            # Update quota
            if quota_info:
                self.update_quota_info(quota_info)
            
            # Show window
            print("[DEBUG] Showing window...")
            self.window.deiconify()
            self.window.lift()
            self.window.attributes("-topmost", True)
            self.window.focus_force()
            
            # Create wave bars nếu chưa có
            if not self.wave_bars_created:
                print("[DEBUG] Creating wave bars...")
                self.window.after(100, self._create_wave_bars)
            
            # Start entrance animation
            self._start_entrance_animation()
            
            print("[OK] Window shown successfully!")
            
        except Exception as e:
            import traceback
            print(f"[ERROR] Show window error: {e}")
            print(traceback.format_exc())
    
    def hide_immediately_safe(self):
        """Ẩn window"""
        try:
            self.is_visible = False
            self._stop_animation()
            
            if self.window:
                self.window.withdraw()
                print("[OK] Window hidden")
                
        except Exception as e:
            print(f"[ERROR] Hide error: {e}")
    
    def update_quota_info(self, quota_info: dict):
        """Update quota info"""
        try:
            if quota_info and self.quota_label:
                current = quota_info.get('current_key_index', 1)
                total = quota_info.get('total_keys', 1)
                remaining = quota_info.get('remaining_requests', '?')
                
                text = f"🔑 API Key #{current}/{total} - {remaining} requests remaining"
                self.quota_label.configure(text=text)
        except:
            pass
    
    def update_wave_data(self, level: float):
        """Cập nhật wave data"""
        try:
            if hasattr(self, 'wave_data'):
                # Smoothing
                if len(self.wave_data) > 0:
                    smoothed = (self.wave_smoothing * level + 
                               (1 - self.wave_smoothing) * self.wave_data[-1])
                else:
                    smoothed = level
                
                # Shift và add - MỚI ở ĐẦU, CŨ ở CUỐI (để wave chạy từ trái sang phải)
                self.wave_data = [smoothed] + self.wave_data[:-1]
                self.current_mic_level = smoothed
                
                # Debug: log khi có audio
                if smoothed > 0.1:
                    print(f"[WAVE] Level: {smoothed:.3f}")
                
        except Exception as e:
            print(f"[ERROR] Wave update error: {e}")
    
    def _create_wave_bars(self):
        """Tạo wave bars đẹp mắt"""
        try:
            if not self.wave_canvas:
                return
            
            # Lấy kích thước thực tế của canvas
            self.wave_canvas.update()
            width = self.wave_canvas.winfo_width()
            height = self.wave_canvas.winfo_height()
            
            # Fallback nếu canvas chưa render
            if width < 100:
                width = 800
            if height < 50:
                height = 130
                
            center_y = height // 2
            num_bars = 120  # Tăng lên 120 bars
            bar_width = width / num_bars
            bar_spacing = 0.5  # Spacing nhỏ giữa bars
            
            print(f"[CANVAS] Size: {width}x{height}, bar_width: {bar_width:.2f}px")
            
            self.wave_bars = []
            
            # Background trong suốt (không vẽ background)
            # self.wave_canvas.create_rectangle(0, 0, width, height, fill="#ffffff", outline="")
            
            # Không vẽ grid và center line (để trong suốt hoàn toàn)
            # for i in range(0, width, 80):
            #     self.wave_canvas.create_line(i, 0, i, height, fill="#f9fafb", width=1)
            # 
            # for i in range(0, height, 25):
            #     self.wave_canvas.create_line(0, i, width, i, fill="#f9fafb", width=1)
            # 
            # self.wave_canvas.create_line(0, center_y, width, center_y, fill="#e5e7eb", width=1, dash=(5, 3))
            
            # Tạo bars mỏng và mịn
            for i in range(num_bars):
                x = i * bar_width
                actual_width = bar_width - bar_spacing
                
                # Bars màu đen
                bar_up = self.wave_canvas.create_rectangle(
                    x, center_y, x + actual_width, center_y,
                    fill="#000000", outline="", width=0  # Màu đen
                )
                bar_down = self.wave_canvas.create_rectangle(
                    x, center_y, x + actual_width, center_y,
                    fill="#000000", outline="", width=0  # Màu đen
                )
                self.wave_bars.append((bar_up, bar_down, x, actual_width))
            
            self.wave_bars_created = True
            print(f"[OK] Created {num_bars} smooth wave bars")
            
        except Exception as e:
            print(f"[ERROR] Create bars error: {e}")
    
    def _start_animation(self):
        """Bắt đầu animation TRONG MAIN THREAD"""
        if self.animation_running:
            return
        
        self.animation_running = True
        print("[ANIM] Animation started (main thread)")
        self._animation_loop()
    
    def _stop_animation(self):
        """Dừng animation"""
        self.animation_running = False
        print("[ANIM] Animation stopped")
    
    def _animation_loop(self):
        """Animation loop - CHẠY TRONG MAIN THREAD"""
        if not self.animation_running or not self.window or not self.is_visible:
            return
        
        try:
            # Vẽ wave
            if self.wave_bars_created and self.wave_bars:
                self._draw_wave()
            
            # Schedule next frame (20 FPS = 50ms)
            self.window.after(50, self._animation_loop)
            
        except Exception as e:
            print(f"[ERROR] Animation error: {e}")
    
    def _draw_wave(self):
        """Vẽ wave realtime với gradient đẹp"""
        try:
            if not self.wave_canvas or not self.wave_bars:
                return
            
            # Lấy height thực tế của canvas
            height = self.wave_canvas.winfo_height()
            if height < 50:
                height = 80  # Fallback
            
            center_y = height // 2
            max_height = center_y - 5  # Margin nhỏ hơn để wave to hơn
            
            # Màu đen cho tất cả bars
            color = "#000000"  # Đen
            
            # VẼ TẤT CẢ bars để đều 2 bên
            for i, (bar_up, bar_down, x, bar_width) in enumerate(self.wave_bars):
                # Lấy level, nếu không có thì = 0
                level = self.wave_data[i] if i < len(self.wave_data) else 0.0
                
                # Power curve nhỏ hơn để wave to hơn
                adjusted_level = pow(level, 0.5)  # Giảm từ 0.65 xuống 0.5
                bar_h = min(adjusted_level * max_height, max_height)
                
                if bar_h > 0.3:  # Ngưỡng thấp để hiện nhiều bars
                    # Bar lên trên
                    self.wave_canvas.coords(
                        bar_up,
                        x, center_y - bar_h,
                        x + bar_width, center_y
                    )
                    self.wave_canvas.itemconfig(bar_up, fill=color)
                    
                    # Bar xuống dưới (đối xứng)
                    self.wave_canvas.coords(
                        bar_down,
                        x, center_y,
                        x + bar_width, center_y + bar_h
                    )
                    self.wave_canvas.itemconfig(bar_down, fill=color)
                else:
                    # Ẩn bars khi level = 0
                    self.wave_canvas.coords(bar_up, x, center_y, x, center_y)
                    self.wave_canvas.coords(bar_down, x, center_y, x, center_y)
                        
        except Exception as e:
            print(f"[ERROR] Draw wave error: {e}")
    
    def _start_entrance_animation(self):
        """Animation khi GUI xuất hiện: Micro slide up, rồi wave fade in"""
        print("[ANIM] Starting entrance animation...")
        try:
            # Kiểm tra attributes
            has_wave = hasattr(self, 'wave_frame')
            has_mic = hasattr(self, 'mic_frame')
            print(f"[ANIM] Has wave_frame: {has_wave}, has mic_frame: {has_mic}")
            
            # Ẩn wave frame ban đầu
            if has_wave:
                print("[ANIM] Hiding wave frame...")
                self.wave_frame.configure(fg_color="#000001")  # Trong suốt ban đầu
                if hasattr(self, 'wave_canvas'):
                    self.wave_canvas.configure(bg="#000001")
            
            # Micro slide up từ dưới
            print("[ANIM] Starting mic slide up...")
            self._animate_mic_slide_up(0)
            
        except Exception as e:
            import traceback
            print(f"[ERROR] Entrance animation error: {e}")
            print(traceback.format_exc())
            # Fallback: hiện bình thường
            self._start_animation()
    
    def _animate_mic_slide_up(self, step):
        """Animate micro slide từ dưới lên (10 steps)"""
        max_steps = 10
        
        if step <= max_steps:
            try:
                # Di chuyển mic từ dưới lên
                offset = (max_steps - step) * 8  # 80px total
                if hasattr(self, 'mic_frame'):
                    self.mic_frame.pack_configure(pady=(0, 12 + offset))
                    if step == 0:
                        print(f"[ANIM] Mic slide step {step}, offset: {offset}px")
                
                # Continue animation
                self.window.after(30, lambda: self._animate_mic_slide_up(step + 1))
                
            except Exception as e:
                print(f"[ERROR] Mic slide error step {step}: {e}")
        else:
            # Micro animation xong, bắt đầu wave fade in
            print("[ANIM] Mic slide complete, starting wave fade...")
            self._animate_wave_fade_in(0)
    
    def _animate_wave_fade_in(self, step):
        """Animate wave frame fade in (10 steps)"""
        max_steps = 10
        
        if step <= max_steps:
            try:
                # Tính alpha (từ trong suốt đến xanh lá)
                alpha = step / max_steps
                
                # Interpolate color từ transparent (#000001) đến xanh (#0fb77f)
                if hasattr(self, 'wave_frame'):
                    if step < max_steps:
                        # Dùng alpha để fade
                        r = int(15 * alpha)
                        g = int(183 * alpha)
                        b = int(127 * alpha)
                        color = f"#{r:02x}{g:02x}{b:02x}"
                        self.wave_frame.configure(fg_color=color)
                        
                        if hasattr(self, 'wave_canvas'):
                            self.wave_canvas.configure(bg=color)
                        
                        if step == 0:
                            print(f"[ANIM] Wave fade step {step}, alpha: {alpha:.2f}")
                    else:
                        # Cuối cùng set màu chính xác
                        self.wave_frame.configure(fg_color="#0fb77f")
                        if hasattr(self, 'wave_canvas'):
                            self.wave_canvas.configure(bg="#0fb77f")
                        print("[ANIM] Wave fade complete")
                
                # Continue animation
                self.window.after(30, lambda: self._animate_wave_fade_in(step + 1))
                
            except Exception as e:
                print(f"[ERROR] Wave fade error step {step}: {e}")
        else:
            # Animation xong, start wave animation
            print("[ANIM] Starting wave bars animation...")
            self._start_animation()
    
    def cleanup(self):
        """Cleanup"""
        try:
            self._stop_animation()
            if self.window:
                self.window.destroy()
        except:
            pass
