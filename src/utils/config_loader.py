"""
Configuration loader utility
"""
import json
import os
from typing import Dict, Any


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """
    Tải cấu hình từ file JSON
    
    Args:
        config_path: Đường dẫn đến file config
        
    Returns:
        Dictionary chứa configuration
        
    Raises:
        FileNotFoundError: Nếu file không tồn tại
        json.JSONDecodeError: Nếu file không phải JSON hợp lệ
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Không tìm thấy file config: {config_path}\n"
            f"Please copy từ config.example.json"
        )
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Validate required sections
    required_sections = ['audio', 'stt', 'hotkeys', 'gui']
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Config thiếu section bắt buộc: {section}")
    
    return config


def save_config(config: Dict[str, Any], config_path: str = "config.json") -> None:
    """
    Lưu cấu hình to file JSON
    
    Args:
        config: Dictionary chứa configuration
        config_path: Đường dẫn đến file config
    """
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
