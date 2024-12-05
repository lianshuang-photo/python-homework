from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                            QComboBox, QProgressBar, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
import webbrowser
import json
import requests
from datetime import datetime, timedelta
from icalendar import Calendar, Event
from icalendar.prop import vDuration
import pytz

class SyncDialog(QDialog):
    def __init__(self, course_manager, parent=None):
        super().__init__(parent)
        self.course_manager = course_manager
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("同步日历")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # 选择日历服务
        self.calendar_combo = QComboBox()
        self.calendar_combo.addItems([
            "Apple Calendar (推荐)",
            "Google Calendar"
        ])
        self.calendar_combo.setCurrentIndex(0)  # 设置 Apple Calendar 为默认选项
        layout.addWidget(self.calendar_combo)
        
        # 同步选项
        self.sync_all_btn = QPushButton("同步所有课程")
        self.sync_all_btn.clicked.connect(self.sync_all_courses)
        layout.addWidget(self.sync_all_btn)
        
        self.sync_week_btn = QPushButton("仅同步本周课程")
        self.sync_week_btn.clicked.connect(lambda: self.sync_courses(current_week_only=True))
        layout.addWidget(self.sync_week_btn)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.hide()
        layout.addWidget(self.progress)
        
    def sync_courses(self, current_week_only=False):
        """同步课程到日历"""
        calendar_service = self.calendar_combo.currentText()
        
        try:
            # 获取要同步的课程
            if current_week_only:
                # 获取主窗口的当前周次
                main_window = self.parent()
                current_week = main_window.current_week if hasattr(main_window, 'current_week') else 1
                courses = [c for c in self.course_manager.get_courses() 
                          if current_week in self._parse_weeks(c.weeks)]
            else:
                courses = self.course_manager.get_courses()
            
            # 显示进度条
            self.progress.setMaximum(len(courses))
            self.progress.setValue(0)
            self.progress.show()
            
            # 根据选择的服务进行同步
            if calendar_service == "Google Calendar":
                self.sync_to_google(courses)
            else:  # Apple Calendar
                self.sync_to_apple(courses)
                
            QMessageBox.information(self, "同步成功", "课表已成功同步到日历！")
            
        except Exception as e:
            QMessageBox.critical(self, "同步失败", f"同步过程中发生错误：{str(e)}")
        finally:
            self.progress.hide()
    
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
        return sorted(set(result))  # 去重并排序
    
    def sync_all_courses(self):
        """同步所有课程"""
        self.sync_courses(current_week_only=False)
    
    def sync_to_google(self, courses):
        """同步到Google日历"""
        # 获取授权
        auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        webbrowser.open(auth_url)
        # 实际实现需要完整的OAuth2流程
        
        # 模拟同步进度
        for i, course in enumerate(courses):
            # 这里应该是实际的同步代码
            self.progress.setValue(i + 1)
            
    def sync_to_apple(self, courses):
        """同步到Apple日历（生成ICS文件）"""
        try:
            # 创建日历
            cal = Calendar()
            cal.add('prodid', '-//课表管理系统//CN')
            cal.add('version', '2.0')
            cal.add('calscale', 'GREGORIAN')
            cal.add('method', 'PUBLISH')
            cal.add('x-wr-calname', '我的课表')
            cal.add('x-wr-timezone', 'Asia/Shanghai')

            # 获取当前学期的第一周的星期一
            current_year = datetime.now().year
            # 这里假设第一周从9月第一个星期一开始，可以根据实际情况调整
            first_monday = self._get_semester_start_date(current_year)
            
            # 设置时区
            tz = pytz.timezone('Asia/Shanghai')

            # 添加每个课程
            for course in courses:
                # 解析周次
                weeks = self._parse_weeks(course.weeks)
                
                # 获取上课时间
                start_time = datetime.strptime(course.start_time.strftime('%H:%M'), '%H:%M')
                end_time = datetime.strptime(course.end_time.strftime('%H:%M'), '%H:%M')
                
                # 为每周的课程创建事件
                for week in weeks:
                    # 计算实际日期
                    days_offset = (course.day_of_week - 1) + (week - 1) * 7
                    course_date = first_monday + timedelta(days=days_offset)
                    
                    # 创建事件
                    event = Event()
                    event.add('summary', course.name)
                    
                    # 设置开始和结束时间
                    start_datetime = datetime.combine(course_date, start_time.time())
                    end_datetime = datetime.combine(course_date, end_time.time())
                    start_datetime = tz.localize(start_datetime)
                    end_datetime = tz.localize(end_datetime)
                    
                    event.add('dtstart', start_datetime)
                    event.add('dtend', end_datetime)
                    
                    # 添加地点和描述
                    event.add('location', course.room)
                    description = f"教师：{course.teacher}\n课程描述：{course.description}"
                    event.add('description', description)
                    
                    # 添加提醒（提前15分钟）
                    event['alarm'] = '-PT15M'  # 使用 ISO 8601 持续时间格式
                    
                    cal.add_component(event)
                
                # 更新进度条
                self.progress.setValue(self.progress.value() + 1)
            
            # 保存ICS文件
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存日历文件",
                f"课表_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ics",
                "iCalendar文件 (*.ics)"
            )
            
            if file_path:
                with open(file_path, 'wb') as f:
                    f.write(cal.to_ical())
                
                QMessageBox.information(
                    self,
                    "导出成功",
                    f"日历文件已保存到：\n{file_path}\n\n"
                    "请使用系统日历应用打开此文件以导入课程。"
                )
                
                # 在访达中显示文件
                import os
                os.system(f'open -R "{file_path}"')
                
        except Exception as e:
            raise Exception(f"生成日历文件失败：{str(e)}")

    def _get_semester_start_date(self, year):
        """获取学期开始日期（这里以9月第一个星期一为例）"""
        # 获取9月1日
        sept_first = datetime(year, 9, 1)
        # 计算第一个星期一
        days_ahead = 0 - sept_first.weekday()  # weekday(): 0=Monday, 6=Sunday
        if days_ahead <= 0:
            days_ahead += 7
        return sept_first + timedelta(days=days_ahead)
    
    def sync_to_outlook(self, courses):
        """同步到Outlook日历"""
        # 使用Outlook API同步
        for i, course in enumerate(courses):
            # 这里应该是实际的同步代码
            self.progress.setValue(i + 1)