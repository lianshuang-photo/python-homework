from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QCalendarWidget, 
                            QLabel, QStackedWidget)
from PyQt6.QtCore import QDate, Qt
from datetime import datetime, timedelta

class CalendarView(QWidget):
    def __init__(self, course_manager, parent=None):
        super().__init__(parent)
        self.course_manager = course_manager
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 创建日历控件
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar.setSelectionMode(QCalendarWidget.SelectionMode.SingleSelection)
        
        # 设置日历样式
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
                border: 1px solid #e2e2e2;
            }
            QCalendarWidget QToolButton {
                color: #333333;
                padding: 6px;
            }
            QCalendarWidget QMenu {
                width: 150px;
                left: 20px;
                color: #333333;
            }
            QCalendarWidget QSpinBox {
                width: 60px;
                font-size: 12px;
                color: #333333;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #333333;
                selection-background-color: #e8f0fe;
                selection-color: #333333;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #f8f9fa;
            }
        """)
        
        # 连接日期选择信号
        self.calendar.selectionChanged.connect(self.on_date_selected)
        
        # 创建课程详情区域
        self.details_widget = QStackedWidget()
        self.empty_label = QLabel("选择日期查看课程")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.details_widget.addWidget(self.empty_label)
        
        layout.addWidget(self.calendar)
        layout.addWidget(self.details_widget)
        
        # 更新日历标记
        self.update_calendar_marks()
        
    def update_calendar_marks(self):
        """更新日历上的课程标记"""
        # 清除现有格式
        self.calendar.setDateTextFormat(QDate(), self.calendar.dateTextFormat(QDate()))
        
        # 获取所有课程
        courses = self.course_manager.get_courses()
        
        # 获取学期第一周的星期一
        first_monday = self._get_semester_start_date()
        
        # 标记有课程的日期
        for course in courses:
            weeks = self._parse_weeks(course.weeks)
            for week in weeks:
                # 计算实际日期
                days_offset = (course.day_of_week - 1) + (week - 1) * 7
                course_date = first_monday + timedelta(days=days_offset)
                
                # 设置日期格式
                date = QDate(course_date.year, course_date.month, course_date.day)
                format = self.calendar.dateTextFormat(date)
                format.setBackground(Qt.GlobalColor.lightGray)
                self.calendar.setDateTextFormat(date, format)
    
    def on_date_selected(self):
        """处理日期选择事件"""
        selected_date = self.calendar.selectedDate()
        # 查找该日期的课程
        courses = self.get_courses_for_date(selected_date)
        
        if courses:
            # 创建课程详情视图
            details_widget = QWidget()
            details_layout = QVBoxLayout(details_widget)
            
            for course in courses:
                course_label = QLabel(
                    f"<b>{course.name}</b><br>"
                    f"时间：{course.start_time.strftime('%H:%M')}-{course.end_time.strftime('%H:%M')}<br>"
                    f"教室：{course.room}<br>"
                    f"教师：{course.teacher}"
                )
                details_layout.addWidget(course_label)
            
            # 替换现有的详情视图
            old_widget = self.details_widget.currentWidget()
            self.details_widget.removeWidget(old_widget)
            old_widget.deleteLater()
            
            self.details_widget.addWidget(details_widget)
        else:
            # 显示空状态
            self.details_widget.setCurrentWidget(self.empty_label)
    
    def get_courses_for_date(self, date):
        """获取指定日期的课程"""
        # 计算当前是第几周
        first_monday = self._get_semester_start_date()
        current_date = datetime(date.year(), date.month(), date.day())
        days_diff = (current_date - first_monday).days
        current_week = days_diff // 7 + 1
        current_weekday = date.dayOfWeek()
        
        # 获取当天的课程
        courses = []
        for course in self.course_manager.get_courses():
            if (current_week in self._parse_weeks(course.weeks) and 
                course.day_of_week == current_weekday):
                courses.append(course)
        
        return courses
    
    def _get_semester_start_date(self):
        """获取学期开始日期（这里以9月第一个星期一为例）"""
        current_year = datetime.now().year
        sept_first = datetime(current_year, 9, 1)
        days_ahead = 0 - sept_first.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return sept_first + timedelta(days=days_ahead)
    
    def _parse_weeks(self, weeks_str: str) -> list:
        """解析周次字符串"""
        result = []
        weeks_str = weeks_str.replace('周', '')
        for part in weeks_str.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                result.extend(range(start, end + 1))
            else:
                result.append(int(part))
        return result 