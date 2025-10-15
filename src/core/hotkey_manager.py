"""
Simple Hotkey Manager - Hold mode with pynput (WORKING VERSION)
"""
from pynput import keyboard
import threading
from typing import Callable


class HotkeyManager:
    """Quản lý hotkey: GIỮ Ctrl+Alt để record, THẢ để dừng"""
    
    def __init__(self, record_key: str = 'ctrl+alt', exit_key: str = 'ctrl+shift+c'):
        """
        Args:
            record_key: Key để hold recording (default: Ctrl+Alt)
            exit_key: Key để exit app (default: Ctrl+Shift+C)
        """
        self.record_key = record_key
        self.exit_key = exit_key
        self.on_start_callback = None
        self.on_stop_callback = None
        self.exit_callback = None
        self.is_registered = False
        
        # Track pressed keys
        self.pressed_keys = set()
        self.listener = None
        
        # Track recording state to prevent multiple stop callbacks
        self.is_hotkey_active = False
        
    def register(self, on_start: Callable, on_stop: Callable, on_exit: Callable):
        """
        Register callbacks
        
        Args:
            on_start: Callback khi bắt đầu giữ hotkey
            on_stop: Callback khi thả hotkey
            on_exit: Callback khi nhấn exit key
        """
        self.on_start_callback = on_start
        self.on_stop_callback = on_stop
        self.exit_callback = on_exit
        
        # Create keyboard listener
        self.listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self.listener.start()
        
        self.is_registered = True
        print(f"[HOTKEY] Registered: HOLD {self.record_key.upper()} to record, RELEASE to stop")
        print(f"[HOTKEY] Press {self.exit_key.upper()} to exit")
        print(f"[HOTKEY] Keyboard listener started")
    
    def _on_key_press(self, key):
        """Callback khi nhấn phím"""
        self.pressed_keys.add(key)
        
        # Check if hotkey is pressed
        if self._is_hotkey_pressed() and not self.is_hotkey_active:
            self.is_hotkey_active = True
            print("[HOTKEY] Ctrl+Alt pressed - Starting recording...")
            if self.on_start_callback:
                threading.Thread(target=self.on_start_callback, daemon=True).start()
        
        # Check exit hotkey
        if self._is_exit_hotkey_pressed():
            print("[HOTKEY] Exit hotkey pressed")
            if self.exit_callback:
                threading.Thread(target=self.exit_callback, daemon=True).start()
    
    def _on_key_release(self, key):
        """Callback khi thả phím"""
        self.pressed_keys.discard(key)
        
        # Check if hotkey is released (only trigger once)
        if not self._is_hotkey_pressed() and self.is_hotkey_active:
            self.is_hotkey_active = False
            print("[HOTKEY] Ctrl+Alt released - Stopping recording...")
            if self.on_stop_callback:
                self.on_stop_callback()
    
    def _is_hotkey_pressed(self) -> bool:
        """Check if Ctrl+Alt is pressed"""
        ctrl_pressed = (keyboard.Key.ctrl_l in self.pressed_keys or 
                       keyboard.Key.ctrl_r in self.pressed_keys)
        alt_pressed = (keyboard.Key.alt_l in self.pressed_keys or 
                      keyboard.Key.alt_r in self.pressed_keys)
        return ctrl_pressed and alt_pressed
    
    def _is_exit_hotkey_pressed(self) -> bool:
        """Check if Ctrl+Shift+C is pressed"""
        ctrl_pressed = (keyboard.Key.ctrl_l in self.pressed_keys or 
                       keyboard.Key.ctrl_r in self.pressed_keys)
        shift_pressed = (keyboard.Key.shift_l in self.pressed_keys or 
                        keyboard.Key.shift_r in self.pressed_keys)
        
        c_pressed = False
        try:
            c_key = keyboard.KeyCode.from_char('c')
            C_key = keyboard.KeyCode.from_char('C')
            c_pressed = (c_key in self.pressed_keys or C_key in self.pressed_keys)
        except:
            pass
        
        return ctrl_pressed and shift_pressed and c_pressed
    
    def unregister(self):
        """Unregister all hotkeys"""
        if self.listener:
            self.listener.stop()
            self.listener = None
        self.is_registered = False
        print("[HOTKEY] Unregistered")
