from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QCalendarWidget,
                            QLabel, QPushButton, QWidget, QScrollArea, QMenu)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QTextCharFormat
from models.course import Course
from typing import List, Dict
from datetime import datetime, timedelta
from .term_settings_dialog import TermSettingsDialog
from models.settings_manager import SettingsManager

class CourseCalendarDialog(QDialog):
    def __init__(self, course_manager, parent=None):
        super().__init__(parent)
        self.course_manager = course_manager
        self.settings_manager = SettingsManager()
        self.setWindowTitle("课程日历")
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.highlight_holidays()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 左侧布局
        left_widget = QWidget()
        left_widget.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(20, 20, 20, 20)
        
        # 设置按钮容器
        settings_container = QWidget()
        settings_container.setObjectName("settingsContainer")
        settings_layout = QHBoxLayout(settings_container)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout.setSpacing(0)
        
        # 设置按钮
        settings_btn = QPushButton("设置开学时间")
        settings_btn.setObjectName("settingsButton")
        settings_btn.clicked.connect(self.show_settings)
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)  # 添加手型光标
        
        # 添加图标
        icon_label = QLabel("⚙️")
        icon_label.setObjectName("settingsIcon")
        
        settings_layout.addWidget(icon_label)
        settings_layout.addWidget(settings_btn)
        left_layout.addWidget(settings_container)
        
        # 日历
        self.calendar = QCalendarWidget(self)
        self.calendar.setMinimumWidth(400)
        self.calendar.clicked.connect(self.on_date_selected)
        self.calendar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.calendar.customContextMenuRequested.connect(self.show_context_menu)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar.setObjectName("customCalendar")
        left_layout.addWidget(self.calendar)
        
        layout.addWidget(left_widget)
        
        # 右侧课程列表
        right_widget = QWidget()
        right_widget.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)
        right_layout.setContentsMargins(20, 20, 20, 20)
        
        # 日期和节假日容器
        date_container = QWidget()
        date_container.setObjectName("dateContainer")
        date_layout = QVBoxLayout(date_container)
        date_layout.setSpacing(5)
        date_layout.setContentsMargins(0, 0, 0, 0)
        
        # 日期标签
        self.date_label = QLabel()
        self.date_label.setObjectName("dateLabel")
        date_layout.addWidget(self.date_label)
        
        # 节假日标签
        self.holiday_label = QLabel()
        self.holiday_label.setObjectName("holidayLabel")
        date_layout.addWidget(self.holiday_label)
        
        right_layout.addWidget(date_container)
        
        # 课程列表滚动区域
        scroll_area = QScrollArea()
        scroll_area.setObjectName("scrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        
        self.course_container = QWidget()
        self.course_layout = QVBoxLayout(self.course_container)
        self.course_layout.setSpacing(10)
        self.course_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area.setWidget(self.course_container)
        right_layout.addWidget(scroll_area)
        
        layout.addWidget(right_widget)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
                border-radius: 20px;
            }
            
            #leftPanel {
                background-color: white;
                border-right: 1px solid #e0e0e0;
                border-top-left-radius: 20px;
                border-bottom-left-radius: 20px;
            }
            
            #rightPanel {
                background-color: white;
                border-top-right-radius: 20px;
                border-bottom-right-radius: 20px;
            }
            
            #settingsContainer {
                background-color: #f8f9fa;
                border-radius: 25px;
                padding: 0;
                margin: 5px 0;
            }
            
            #settingsContainer:hover {
                background-color: #e9ecef;
            }
            
            #settingsButton {
                background-color: transparent;
                border: none;
                border-radius: 25px;
                padding: 12px 20px 12px 5px;
                color: #444;
                font-size: 14px;
                text-align: left;
            }
            
            #settingsIcon {
                font-size: 16px;
                padding: 0 15px;
            }
            
            #customCalendar {
                background-color: white;
                border: none;
                border-radius: 15px;
            }
            
            #customCalendar QWidget {
                alternate-background-color: #f8f9fa;
            }
            
            /* 月份年份选择区域 */
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: transparent;
                padding: 8px;
            }
            
            /* 月份年份下拉框 */
            QCalendarWidget QSpinBox,
            QCalendarWidget QComboBox {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 15px;
                padding: 5px 10px;
                min-width: 80px;
                margin: 0 4px;
            }
            
            /* 导航按钮（上个月/下个月） */
            QCalendarWidget QToolButton {
                color: #444;
                background-color: transparent;
                border-radius: 20px;
                padding: 8px;
                margin: 2px;
                min-width: 35px;
                min-height: 35px;
            }
            
            QCalendarWidget QToolButton::menu-indicator {
                image: none;
            }
            
            /* 月份导航按钮 */
            QCalendarWidget QToolButton#qt_calendar_prevmonth,
            QCalendarWidget QToolButton#qt_calendar_nextmonth {
                background-color: transparent;
                margin: 0 8px;
            }
            
            QCalendarWidget QToolButton#qt_calendar_prevmonth {
                qproperty-icon: none;
                qproperty-text: "◀";
                font-size: 18px;
                color: #666;
            }
            
            QCalendarWidget QToolButton#qt_calendar_nextmonth {
                qproperty-icon: none;
                qproperty-text: "▶";
                font-size: 18px;
                color: #666;
            }
            
            QCalendarWidget QToolButton#qt_calendar_prevmonth:hover,
            QCalendarWidget QToolButton#qt_calendar_nextmonth:hover {
                background-color: #f0f2f5;
                color: #333;
            }
            
            QCalendarWidget QToolButton:pressed {
                background-color: #e9ecef;
            }
            
            /* 日历网格 */
            QCalendarWidget QTableView {
                outline: none;
                selection-background-color: #007bff;
                selection-color: white;
            }
            
            QCalendarWidget QTableView::item:hover {
                background-color: #e9ecef;
                border-radius: 15px;
            }
            
            QCalendarWidget QTableView::item:selected {
                background-color: #007bff;
                color: white;
                border-radius: 15px;
            }
            
            /* 星期标题行 */
            QCalendarWidget QTableView QHeaderView::section {
                background-color: transparent;
                color: #666;
                font-weight: bold;
                padding: 5px;
                border: none;
            }
            
            /* 日期单元格 */
            QCalendarWidget QAbstractItemView:enabled {
                color: #444;
                background-color: white;
                selection-background-color: #007bff;
                selection-color: white;
            }
            
            QCalendarWidget QAbstractItemView:disabled {
                color: #999;
            }
            
            #dateContainer {
                background-color: #f8f9fa;
                border-radius: 15px;
                padding: 15px;
                margin-bottom: 10px;
            }
            
            #dateLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333;
            }
            
            #holidayLabel {
                font-size: 14px;
                color: #e74c3c;
            }
            
            #scrollArea {
                background-color: transparent;
            }
            
            QScrollBar:vertical {
                border: none;
                background-color: #f0f0f0;
                width: 6px;
                border-radius: 3px;
                margin: 0;
            }
            
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 3px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                height: 0;
                background: none;
            }
            
            /* 课程卡片样式 */
            QWidget#courseCard {
                border-radius: 15px;
            }
        """)
        
        # 初始化显示当前日期的课程
        self.on_date_selected(QDate.currentDate())
        
    def show_settings(self):
        """显示设置对话框"""
        dialog = TermSettingsDialog(self.settings_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 重新计算周次并刷新显示
            self.highlight_holidays()
            self.on_date_selected(self.calendar.selectedDate())
            
    def show_context_menu(self, pos):
        """显示右键菜单"""
        selected_date = self.calendar.selectedDate()
        date = datetime(selected_date.year(), selected_date.month(), selected_date.day())
        holiday = self.settings_manager.get_holiday(date)
        
        menu = QMenu(self)
        if holiday:
            remove_action = menu.addAction(f"删除节假日：{holiday['name']}")
            remove_action.triggered.connect(lambda: self.remove_holiday(date))
        else:
            add_action = menu.addAction("添加为节假日")
            add_action.triggered.connect(lambda: self.add_holiday(date))
            
        menu.exec(self.calendar.mapToGlobal(pos))
        
    def add_holiday(self, date: datetime):
        """添加节假日"""
        self.settings_manager.add_holiday(date, "节假日")
        self.highlight_holidays()
        self.on_date_selected(self.calendar.selectedDate())
        
    def remove_holiday(self, date: datetime):
        """删除节假日"""
        self.settings_manager.remove_holiday(date)
        self.highlight_holidays()
        self.on_date_selected(self.calendar.selectedDate())
        
    def highlight_holidays(self):
        """高亮显示节假日"""
        # 重置所有日期格式
        default_format = QTextCharFormat()
        self.calendar.setDateTextFormat(QDate(), default_format)
        
        # 设置节假日高亮
        holiday_format = QTextCharFormat()
        holiday_format.setBackground(QColor("#ffebee"))
        holiday_format.setForeground(QColor("#e74c3c"))
        
        # 获取当前显示的年份
        current_year = self.calendar.selectedDate().year()
        
        # 遍历整年的日期
        current_date = datetime(current_year, 1, 1)
        while current_date.year == current_year:
            holiday = self.settings_manager.get_holiday(current_date)
            if holiday:
                date = QDate(current_date.year, current_date.month, current_date.day)
                self.calendar.setDateTextFormat(date, holiday_format)
            current_date += timedelta(days=1)
        
    def on_date_selected(self, date: QDate):
        """当选择日期时更新课程显示"""
        # 更新日期标签
        self.date_label.setText(date.toString("yyyy年MM月dd日"))
        
        # 显示节假日信息
        selected_date = datetime(date.year(), date.month(), date.day())
        holiday = self.settings_manager.get_holiday(selected_date)
        if holiday:
            self.holiday_label.setText(f"🎉 {holiday['name']}")
            self.holiday_label.show()
        else:
            self.holiday_label.hide()
        
        # 清空现有课程显示
        while self.course_layout.count():
            child = self.course_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # 获取选中日期是第几周和星期几
        term_start = self.settings_manager.get_term_start()
        term_start_date = QDate(term_start.year, term_start.month, term_start.day)
        week = date.weekNumber()[0] - term_start_date.weekNumber()[0] + 1
        day_of_week = date.dayOfWeek()
        
        # 获取当天的课程
        courses = self.course_manager.get_courses()
        day_courses = [
            course for course in courses
            if course.day_of_week == day_of_week and
            week in self._parse_weeks(course.weeks)
        ]
        
        # 按时间排序
        day_courses.sort(key=lambda x: x.start_time)
        
        # 显示课程
        if not day_courses:
            no_course_label = QLabel("今天没有课程")
            no_course_label.setStyleSheet("color: #666; padding: 20px;")
            self.course_layout.addWidget(no_course_label)
        else:
            for course in day_courses:
                course_card = self._create_course_card(course)
                self.course_layout.addWidget(course_card)
                
        # 添加底部弹性空间
        self.course_layout.addStretch()
        
    def _create_course_card(self, course: Course) -> QWidget:
        """创建课程卡片"""
        card = QWidget()
        card.setObjectName("courseCard")
        
        # 生成柔和的背景色
        base_color = QColor(course.color)
        light_color = QColor(
            min(base_color.red() + 30, 255),
            min(base_color.green() + 30, 255),
            min(base_color.blue() + 30, 255),
            30  # 降低不透明度使颜色更柔和
        )
        
        card.setStyleSheet(f"""
            QWidget#courseCard {{
                background-color: {light_color.name()};
                border-radius: 15px;
                padding: 15px;
            }}
            QLabel {{
                color: #444;
                background: transparent;
            }}
            QLabel#courseTitle {{
                font-size: 16px;
                font-weight: bold;
                color: #333;
            }}
            QLabel#courseInfo {{
                font-size: 14px;
                color: #666;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 课程名称
        name_label = QLabel(course.name)
        name_label.setObjectName("courseTitle")
        layout.addWidget(name_label)
        
        # 时间信息
        time_label = QLabel(f"⏰ {course.start_time.strftime('%H:%M')}-{course.end_time.strftime('%H:%M')}")
        time_label.setObjectName("courseInfo")
        layout.addWidget(time_label)
        
        # 教室信息
        if course.room:
            room_label = QLabel(f"📍 {course.room}")
            room_label.setObjectName("courseInfo")
            layout.addWidget(room_label)
        
        # 教师信息
        if course.teacher:
            teacher_label = QLabel(f"👤 {course.teacher}")
            teacher_label.setObjectName("courseInfo")
            layout.addWidget(teacher_label)
        
        return card
        
    def _parse_weeks(self, weeks_str: str) -> List[int]:
        """解析周次字符串，如 "1-16周" -> [1,2,3,...,16]"""
        result = []
        weeks_str = weeks_str.replace('周', '')
        for part in weeks_str.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                result.extend(range(start, end + 1))
            else:
                result.append(int(part))
        return result
