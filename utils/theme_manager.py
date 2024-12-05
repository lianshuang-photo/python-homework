from typing import Dict, Any
from PyQt6.QtGui import QColor

class ThemeManager:
    """主题管理器"""
    
    # 预设主题
    THEMES = {
        "默认主题": {
            "name": "默认主题",
            "primary": "#0366d6",          # GitHub蓝
            "background": "#ffffff",
            "surface": "#f5f5f5",
            "border": "#e2e2e2",
            "text": "#333333",
            "text_secondary": "#666666",
            "hover": "#f5f5f5",
            "accent": "#0358c9",
        },
        "薰衣草": {
            "name": "薰衣草",
            "primary": "#9d8cd6",          # 淡紫色
            "background": "#f8f7fc",       # 极淡的紫色背景
            "surface": "#f0eef8",          # 淡紫色表面
            "border": "#e6e3f4",           # 淡紫色边框
            "text": "#4a4360",             # 深紫色文字
            "text_secondary": "#7a7490",    # 次要文字
            "hover": "#ece9f7",            # 悬停色
            "accent": "#7b6cc5",           # 强调色
        },
        "森林绿": {
            "name": "森林绿",
            "primary": "#238636",          # GitHub绿
            "background": "#ffffff",
            "surface": "#f5f5f5",
            "border": "#e2e2e2",
            "text": "#333333",
            "text_secondary": "#666666",
            "hover": "#f0f9f1",
            "accent": "#1a7f2d",
        },
        "珊瑚粉": {
            "name": "珊瑚粉",
            "primary": "#f85149",          # GitHub红
            "background": "#ffffff",
            "surface": "#f5f5f5",
            "border": "#e2e2e2",
            "text": "#333333",
            "text_secondary": "#666666",
            "hover": "#fff5f5",
            "accent": "#e53e3e",
        },
        "深海蓝": {
            "name": "深海蓝",
            "primary": "#0ea5e9",          # Tailwind蓝
            "background": "#ffffff",
            "surface": "#f5f5f5",
            "border": "#e2e2e2",
            "text": "#333333",
            "text_secondary": "#666666",
            "hover": "#f0f9ff",
            "accent": "#0284c7",
        }
    }
    
    def __init__(self):
        self.current_theme = "默认主题"
    
    def get_theme(self, theme_name: str = None) -> Dict[str, str]:
        """获取主题配置"""
        return self.THEMES.get(theme_name or self.current_theme)
    
    def set_theme(self, theme_name: str):
        """设置当前主题"""
        if theme_name in self.THEMES:
            self.current_theme = theme_name
    
    def get_stylesheet(self, theme_name: str = None) -> str:
        """生成主题样式表"""
        theme = self.get_theme(theme_name)
        
        return f"""
        /* 主窗口样式 */
        QMainWindow {{
            background-color: {theme['background']};
        }}
        
        /* 工具栏样式 */
        #toolbar {{
            background-color: {theme['background']};
            border-bottom: 1px solid {theme['border']};
            padding: 8px 16px;
        }}
        
        /* 按钮基础样式 */
        QPushButton {{
            background-color: {theme['background']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 13px;
            min-width: 70px;
        }}
        
        QPushButton:hover {{
            background-color: {theme['hover']};
            border: 1px solid {theme['primary']};
        }}
        
        QPushButton:pressed {{
            background-color: {theme['surface']};
        }}
        
        /* 选中状态的标签页按钮 */
        QPushButton#selectedTab {{
            background-color: {theme['hover']};
            color: {theme['primary']};
            border: 1px solid {theme['primary']};
        }}
        
        /* 主要操作按钮 */
        QPushButton#addCourseBtn {{
            background-color: {theme['primary']};
            color: #ffffff;
            border: none;
        }}
        
        QPushButton#addCourseBtn:hover {{
            background-color: {theme['accent']};
        }}
        
        /* 周次选择器样式 */
        #weekSelector {{
            background-color: {theme['surface']};
            border: 1px solid {theme['border']};
            border-radius: 6px;
            padding: 2px;
            margin: 0 8px;
        }}
        
        /* 周次导航按钮 */
        #weekNavBtn {{
            background-color: transparent;
            border: none;
            min-width: 24px;
            padding: 4px;
            border-radius: 4px;
            color: {theme['text_secondary']};
        }}
        
        #weekNavBtn:hover {{
            background-color: {theme['hover']};
            border: 1px solid {theme['border']};
        }}
        
        /* 周次下拉框 */
        QComboBox {{
            background-color: {theme['background']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            padding: 6px 12px;
            border-radius: 6px;
            min-width: 100px;
        }}
        
        QComboBox:hover {{
            border: 1px solid {theme['primary']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border: none;
            width: 20px;
        }}
        
        /* 下拉列表样式 */
        QComboBox QAbstractItemView {{
            background-color: {theme['background']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            border-radius: 6px;
            padding: 4px;
            selection-background-color: {theme['primary']};
            selection-color: white;
        }}
        
        QComboBox QAbstractItemView::item {{
            padding: 6px 12px;
            min-height: 24px;
        }}
        
        QComboBox QAbstractItemView::item:hover {{
            background-color: {theme['hover']};
        }}
        
        QComboBox QAbstractItemView::item:selected {{
            background-color: {theme['primary']};
            color: white;
        }}
        
        /* 搜索框样式 */
        QLineEdit {{
            background-color: {theme['surface']};
            border: 1px solid {theme['border']};
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 13px;
            color: {theme['text']};
        }}
        
        QLineEdit:focus {{
            border: 1px solid {theme['primary']};
        }}
        
        /* 表格样式 */
        QTableWidget {{
            background-color: {theme['background']};
            border: none;
            gridline-color: {theme['border']};
        }}
        
        QTableWidget::item {{
            padding: 2px;
        }}
        
        /* 课程卡片样式 */
        #courseCard {{
            background-color: {theme['background']};
            border: 1px solid {theme['border']};
            border-radius: 6px;
            margin: 2px;
        }}
        
        #courseCard:hover {{
            border: 1px solid {theme['primary']};
            background-color: {theme['hover']};
        }}
        
        #courseName {{
            font-size: 12px;
            font-weight: 500;
            color: {theme['text']};
        }}
        
        #infoText {{
            color: {theme['text_secondary']};
            font-size: 11px;
        }}
        
        /* 空单元格悬停效果 */
        QTableWidget::item:empty:hover {{
            background-color: {theme['hover']};
            border: 1px dashed {theme['border']};
            border-radius: 6px;
        }}
        """
    