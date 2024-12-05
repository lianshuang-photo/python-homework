from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTabWidget, QWidget,
                            QTableWidget, QTableWidgetItem, QLabel, QHeaderView)
from PyQt6.QtCore import Qt
from collections import Counter

class StatisticsDialog(QDialog):
    def __init__(self, course_manager, parent=None):
        super().__init__(parent)
        self.course_manager = course_manager
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("课程统计")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 基本统计
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        courses = self.course_manager.get_courses()
        
        # 总课程数
        total_label = QLabel(f"总课程数：{len(courses)}门")
        total_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px 0;")
        basic_layout.addWidget(total_label)
        
        # 每天课程数统计
        daily_stats = Counter(course.day_of_week for course in courses)
        days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        daily_text = "每天课程数：\n"
        for i, day in enumerate(days, 1):
            daily_text += f"{day}: {daily_stats[i]}门\n"
        daily_label = QLabel(daily_text)
        daily_label.setStyleSheet("font-size: 13px; margin: 10px 0;")
        basic_layout.addWidget(daily_label)
        
        # 课程名称统计
        course_table = QTableWidget()
        course_table.setColumnCount(3)
        course_table.setHorizontalHeaderLabels(["课程名称", "上课次数", "任课教师"])
        
        # 统计课程信息
        course_stats = {}
        for course in courses:
            if course.name not in course_stats:
                course_stats[course.name] = {
                    'count': 1,
                    'teachers': {course.teacher}
                }
            else:
                course_stats[course.name]['count'] += 1
                course_stats[course.name]['teachers'].add(course.teacher)
        
        course_table.setRowCount(len(course_stats))
        for i, (name, info) in enumerate(sorted(course_stats.items())):
            course_table.setItem(i, 0, QTableWidgetItem(name))
            course_table.setItem(i, 1, QTableWidgetItem(str(info['count'])))
            course_table.setItem(i, 2, QTableWidgetItem(', '.join(info['teachers'])))
        
        # 设置表格样式
        course_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        course_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #e0e0e0;
            }
        """)
        basic_layout.addWidget(course_table)
        
        tab_widget.addTab(basic_tab, "基本统计")
        
        # 教师统计
        teacher_tab = QWidget()
        teacher_layout = QVBoxLayout(teacher_tab)
        teacher_stats = Counter(course.teacher for course in courses)
        
        teacher_table = QTableWidget()
        teacher_table.setColumnCount(2)
        teacher_table.setHorizontalHeaderLabels(["教师", "课程数"])
        teacher_table.setRowCount(len(teacher_stats))
        
        for i, (teacher, count) in enumerate(teacher_stats.most_common()):
            teacher_table.setItem(i, 0, QTableWidgetItem(teacher))
            teacher_table.setItem(i, 1, QTableWidgetItem(str(count)))
        
        teacher_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        teacher_layout.addWidget(teacher_table)
        tab_widget.addTab(teacher_tab, "教师统计")
        
        # 教室统计
        room_tab = QWidget()
        room_layout = QVBoxLayout(room_tab)
        room_stats = Counter(course.room for course in courses)
        
        room_table = QTableWidget()
        room_table.setColumnCount(2)
        room_table.setHorizontalHeaderLabels(["教室", "使用次数"])
        room_table.setRowCount(len(room_stats))
        
        for i, (room, count) in enumerate(room_stats.most_common()):
            room_table.setItem(i, 0, QTableWidgetItem(room))
            room_table.setItem(i, 1, QTableWidgetItem(str(count)))
        
        room_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        room_layout.addWidget(room_table)
        tab_widget.addTab(room_tab, "教室统计")
        
        layout.addWidget(tab_widget) 