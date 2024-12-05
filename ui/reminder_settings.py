from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QSpinBox, QComboBox, QFileDialog)
from PyQt6.QtCore import Qt
import json
import os

class ReminderSettings(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        self.setWindowTitle("提醒设置")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # 提醒时间设置
        time_layout = QHBoxLayout()
        time_label = QLabel("提前提醒时间：")
        self.time_spin = QSpinBox()
        self.time_spin.setRange(1, 60)
        self.time_spin.setValue(15)
        time_unit = QLabel("分钟")
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_spin)
        time_layout.addWidget(time_unit)
        time_layout.addStretch()
        layout.addLayout(time_layout)
        
        # 提醒声音设置
        sound_layout = QHBoxLayout()
        sound_label = QLabel("提醒声音：")
        self.sound_combo = QComboBox()
        self.sound_combo.addItems(["默认", "无声"])
        self.sound_combo.currentTextChanged.connect(self.on_sound_changed)
        sound_layout.addWidget(sound_label)
        sound_layout.addWidget(self.sound_combo)
        
        # 自定义声音按钮
        self.custom_sound_btn = QPushButton("选择声音文件")
        self.custom_sound_btn.clicked.connect(self.choose_sound_file)
        sound_layout.addWidget(self.custom_sound_btn)
        sound_layout.addStretch()
        layout.addLayout(sound_layout)
        
        # 确定取消按钮
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addStretch()
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
    def load_settings(self):
        """加载设置"""
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                self.time_spin.setValue(settings.get('reminder_time', 15))
                self.sound_combo.setCurrentText(settings.get('sound_type', '默认'))
        except:
            pass
            
    def save_settings(self):
        """保存设置"""
        settings = {
            'reminder_time': self.time_spin.value(),
            'sound_type': self.sound_combo.currentText()
        }
        with open('settings.json', 'w') as f:
            json.dump(settings, f)
            
    def choose_sound_file(self):
        """选择自定义声音文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择声音文件",
            "",
            "音频文件 (*.mp3 *.wav)"
        )
        if file_path:
            self.sound_combo.addItem(file_path)
            self.sound_combo.setCurrentText(file_path)
            
    def on_sound_changed(self, text):
        """声音选择改变时的处理"""
        self.custom_sound_btn.setEnabled(text != "无声") 