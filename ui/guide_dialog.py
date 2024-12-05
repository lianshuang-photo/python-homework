from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                            QScrollArea, QWidget)
from PyQt6.QtCore import Qt

class GuideDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("使用指南")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # 添加指南内容
        guides = [
            ("基本操作", [
                "双击空白单元格添加课程",
                "右键点击课程卡片进行编辑或删除",
                "使用搜索框快速查找课程（Ctrl+F）",
                "使用左右箭头或Alt+方向键切换周次"
            ]),
            ("快捷键", [
                "Ctrl+N：添加新课程",
                "Ctrl+E：导出课表",
                "Ctrl+I：导入课表",
                "Ctrl+F：搜索课程",
                "Alt+←/→：切换周次"
            ]),
            ("数据管理", [
                "定期备份数据（设置-数据备份）",
                "导出课表支持PDF和PNG格式",
                "可以将课表同步到系统日历",
                "支持课表分享功能"
            ])
        ]
        
        for section, items in guides:
            # 添加分节标题
            title = QLabel(section)
            title.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #333;
                    margin-top: 10px;
                }
            """)
            scroll_layout.addWidget(title)
            
            # 添加具体条目
            for item in items:
                item_label = QLabel(f"• {item}")
                item_label.setWordWrap(True)
                scroll_layout.addWidget(item_label)
        
        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        scroll.setWidgetResizable(True)
        
        layout.addWidget(scroll)
        
        # 添加关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn) 