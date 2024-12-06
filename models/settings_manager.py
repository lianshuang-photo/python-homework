import json
from datetime import datetime
from typing import Dict, Optional

class SettingsManager:
    def __init__(self, settings_file: str = "settings.json"):
        self.settings_file = settings_file
        self.settings = self._load_settings()
        
    def _load_settings(self) -> dict:
        """加载设置"""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # 默认设置
            return {
                "term_start": "2024-02-26",  # 默认开学时间
                "holidays": {
                    "2024-04-04": {"name": "清明节", "type": "holiday"},
                    "2024-04-05": {"name": "清明节", "type": "holiday"},
                    "2024-04-06": {"name": "清明节", "type": "holiday"},
                    "2024-05-01": {"name": "劳动节", "type": "holiday"},
                    "2024-05-02": {"name": "劳动节", "type": "holiday"},
                    "2024-05-03": {"name": "劳动节", "type": "holiday"},
                    "2024-05-04": {"name": "劳动节", "type": "holiday"},
                    "2024-05-05": {"name": "劳动节", "type": "holiday"},
                    "2024-06-10": {"name": "端午节", "type": "holiday"},
                    "2024-06-11": {"name": "端午节", "type": "holiday"},
                    "2024-06-12": {"name": "端午节", "type": "holiday"},
                }
            }
    
    def save_settings(self):
        """保存设置"""
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)
            
    def get_term_start(self) -> datetime:
        """获取开学时间"""
        date_str = self.settings.get("term_start", "2024-02-26")
        return datetime.strptime(date_str, "%Y-%m-%d")
    
    def set_term_start(self, date: datetime):
        """设置开学时间"""
        self.settings["term_start"] = date.strftime("%Y-%m-%d")
        self.save_settings()
        
    def get_holiday(self, date: datetime) -> Optional[Dict]:
        """获取指定日期的节假日信息"""
        date_str = date.strftime("%Y-%m-%d")
        return self.settings.get("holidays", {}).get(date_str)
        
    def add_holiday(self, date: datetime, name: str, holiday_type: str = "holiday"):
        """添加节假日"""
        date_str = date.strftime("%Y-%m-%d")
        if "holidays" not in self.settings:
            self.settings["holidays"] = {}
        self.settings["holidays"][date_str] = {
            "name": name,
            "type": holiday_type
        }
        self.save_settings()
        
    def remove_holiday(self, date: datetime):
        """删除节假日"""
        date_str = date.strftime("%Y-%m-%d")
        if date_str in self.settings.get("holidays", {}):
            del self.settings["holidays"][date_str]
            self.save_settings()
