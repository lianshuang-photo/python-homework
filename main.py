import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from ui.main_window import MainWindow
from utils.config_manager import ConfigManager

def main():
    try:
        app = QApplication(sys.argv)
        
        # 确保必要的目录存在
        os.makedirs('ui/styles', exist_ok=True)
        
        # 创建配置管理器
        config_manager = ConfigManager()
        
        # 创建主窗口
        window = MainWindow()
        window.config_manager = config_manager
        window.show()
        
        sys.exit(app.exec())
    except Exception as e:
        QMessageBox.critical(None, "错误", f"程序启动失败：{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
