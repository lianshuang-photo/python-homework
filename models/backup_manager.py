from datetime import datetime
import json
import os
import shutil
import zipfile

class BackupManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.backup_dir = "backups"
        
        # 创建备份目录
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_backup(self) -> str:
        """创建数据备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.zip"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        with zipfile.ZipFile(backup_path, 'w') as backup_zip:
            # 备份数据库
            backup_zip.write(self.db_path, "courses.db")
            
            # 备份设置文件
            if os.path.exists("settings.json"):
                backup_zip.write("settings.json")
        
        return backup_path
    
    def restore_backup(self, backup_path: str) -> bool:
        """从备份恢复数据"""
        try:
            with zipfile.ZipFile(backup_path, 'r') as backup_zip:
                # 恢复前创建临时备份
                self.create_backup()
                
                # 恢复数据库
                backup_zip.extract("courses.db", "temp")
                shutil.move("temp/courses.db", self.db_path)
                
                # 恢复设置
                if "settings.json" in backup_zip.namelist():
                    backup_zip.extract("settings.json", ".")
                
                # 清理临时文件
                shutil.rmtree("temp")
                return True
        except Exception as e:
            print(f"恢复备份失败: {e}")
            return False 