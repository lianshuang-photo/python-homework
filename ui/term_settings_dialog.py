from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QCalendarWidget, QMessageBox)
from PyQt6.QtCore import QDate
from models.settings_manager import SettingsManager
from datetime import datetime

class TermSettingsDialog(QDialog):
    def __init__(self, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle("学期设置")
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 开学时间选择
        term_label = QLabel("请选择开学时间：")
        term_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(term_label)
        
        # 日历控件
        self.calendar = QCalendarWidget(self)
        current_term_start = self.settings_manager.get_term_start()
        self.calendar.setSelectedDate(QDate(
            current_term_start.year,
            current_term_start.month,
            current_term_start.day
        ))
        layout.addWidget(self.calendar)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
    def save_settings(self):
        """保存设置"""
        selected_date = self.calendar.selectedDate()
        term_start = datetime(
            selected_date.year(),
            selected_date.month(),
            selected_date.day()
        )
        
        # 保存开学时间
        self.settings_manager.set_term_start(term_start)
        
        QMessageBox.information(
            self,
            "设置成功",
            f"开学时间已设置为：{term_start.strftime('%Y年%m月%d日')}"
        )
        self.accept()
