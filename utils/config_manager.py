import json
import os
from typing import Dict, Any

class ConfigManager:
    """配置文件管理类"""
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return self.get_default_config()
        return self.get_default_config()
        
    def save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
            
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'reminder': {
                'advance_time': 15,  # 提前提醒时间（分钟）
                'show_notification': True,  # 显示桌面通知
                'play_sound': True,  # 播放提示音
            },
            'theme': {
                'primary_color': '#1a73e8',  # 主题色
                'background_color': '#ffffff',  # 背景色
                'text_color': '#333333',  # 文字颜色
            },
            'display': {
                'start_week': 1,  # 起始周
                'total_weeks': 20,  # 总周数
            }
        }
        
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        try:
            parts = key.split('.')
            value = self.config
            for part in parts:
                value = value[part]
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, key: str, value: Any):
        """设置配置项"""
        parts = key.split('.')
        config = self.config
        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            config = config[part]
        config[parts[-1]] = value
        self.save_config() 