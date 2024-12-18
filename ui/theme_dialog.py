from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QFrame, QWidget, QApplication)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer, QEvent
from utils.theme_manager import ThemeManager

class ThemeDialog(QDialog):
    """主题设置对话框"""
    theme_changed = pyqtSignal(str)  # 主题改变信号
    
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Window)  # 使用Window类型
        self.theme_manager = ThemeManager()
        self.theme_cards = []  # 保存主题卡片的引用
        
        # 设置窗口属性
        self.setWindowTitle("主题设置")
        self.setFixedSize(800, 400)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setModal(True)  # 使用setModal替代setWindowModality
        
        # 设置窗口位置到父窗口中央
        if parent:
            parent_center = parent.geometry().center()
            self.setGeometry(
                parent_center.x() - 400,
                parent_center.y() - 200,
                800,
                400
            )
        
        # 初始化UI
        self.init_ui()
        
        # 安装事件过滤器
        self.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """事件过滤器，用于处理特定事件"""
        if event.type() == QEvent.Type.Show:
            QTimer.singleShot(100, self.update)  # 延迟更新窗口
        return super().eventFilter(obj, event)
    
    def showEvent(self, event):
        """显示事件处理"""
        super().showEvent(event)
        QTimer.singleShot(0, self.raise_)  # 确保窗口在最前面
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # 标题
        title = QLabel("选择主题")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #202124;
            margin-bottom: 16px;
        """)
        layout.addWidget(title)
        
        # 主题预览区
        themes_container = QWidget()
        themes_layout = QHBoxLayout(themes_container)
        themes_layout.setSpacing(16)
        themes_layout.setContentsMargins(0, 0, 0, 0)
        
        # 使用列表保存主题卡片的引用
        self.theme_cards = []
        
        for theme_name, theme in ThemeManager.THEMES.items():
            theme_card = self.create_theme_card(theme_name, theme)
            self.theme_cards.append(theme_card)  # 保存引用
            themes_layout.addWidget(theme_card)
            
        layout.addWidget(themes_container)
        
        # 底部按钮
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                color: #202124;
                border: 1px solid #dadce0;
                padding: 8px 24px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f1f3f4;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addWidget(button_container)
    
    def create_theme_card(self, theme_name: str, theme: dict) -> QFrame:
        """创建主题预览卡片"""
        card = QFrame()
        card.setObjectName("themeCard")
        
        # 为默认主题添加特殊样式
        is_default = theme_name == "默认主题"
        
        # 设置卡片样式
        card.setStyleSheet(f"""
            QFrame#themeCard {{
                background-color: {theme['background']};
                border: {f"2px solid {theme['primary']}" if is_default else f"1px solid {theme['border']}"};
                border-radius: 8px;
            }}
            QFrame#themeCard:hover {{
                border: 2px solid {theme['primary']};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # 主题名称和标签
        name_container = QWidget()
        name_layout = QHBoxLayout(name_container)
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(8)
        
        name_label = QLabel(theme_name)
        name_label.setStyleSheet(f"""
            color: {theme['text']};
            font-size: 14px;
            font-weight: bold;
        """)
        name_layout.addWidget(name_label)
        
        if is_default:
            default_label = QLabel("默认")
            default_label.setStyleSheet(f"""
                color: {theme['primary']};
                font-size: 12px;
                padding: 2px 8px;
                background: {theme['hover']};
                border-radius: 4px;
            """)
            name_layout.addWidget(default_label)
        
        name_layout.addStretch()
        layout.addWidget(name_container)
        
        # 颜色预览
        colors_container = QWidget()
        colors_layout = QHBoxLayout(colors_container)
        colors_layout.setSpacing(8)
        colors_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加颜色预览
        for color_name, color in [
            ("主色调", theme['primary']),
            ("强调色", theme['accent'])
        ]:
            color_widget = QWidget()
            color_layout = QVBoxLayout(color_widget)
            color_layout.setSpacing(4)
            color_layout.setContentsMargins(0, 0, 0, 0)
            
            color_preview = QFrame()
            color_preview.setFixedSize(32, 32)
            color_preview.setStyleSheet(f"""
                background-color: {color};
                border-radius: 4px;
                border: 1px solid {theme['border']};
            """)
            
            color_label = QLabel(color_name)
            color_label.setStyleSheet(f"""
                color: {theme['text_secondary']};
                font-size: 12px;
            """)
            color_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            color_layout.addWidget(color_preview, alignment=Qt.AlignmentFlag.AlignCenter)
            color_layout.addWidget(color_label, alignment=Qt.AlignmentFlag.AlignCenter)
            colors_layout.addWidget(color_widget)
        
        layout.addWidget(colors_container)
        
        # 预览文本
        preview_text = QLabel("预览文本")
        preview_text.setStyleSheet(f"""
            color: {theme['text']};
            font-size: 13px;
            padding: 8px;
            background: {theme['surface']};
            border-radius: 4px;
        """)
        preview_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(preview_text)
        
        # 应用按钮
        apply_btn = QPushButton("应用主题")
        apply_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['primary']};
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {theme['accent']};
            }}
        """)
        apply_btn.clicked.connect(lambda: self.apply_theme(theme_name))
        layout.addWidget(apply_btn)
        
        return card
    
    def apply_theme(self, theme_name: str):
        """应用主题"""
        self.theme_changed.emit(theme_name)
        self.close()
    
    def closeEvent(self, event):
        """关闭事件处理"""
        # 清理资源
        self.theme_cards.clear()
        event.accept()