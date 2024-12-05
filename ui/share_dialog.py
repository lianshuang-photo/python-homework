from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                            QComboBox, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
import json
from datetime import datetime
import os

class ShareDialog(QDialog):
    def __init__(self, course_manager, parent=None):
        super().__init__(parent)
        self.course_manager = course_manager
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("分享课表")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # 分享方式选择
        self.share_combo = QComboBox()
        self.share_combo.addItems([
            "导出课表文件", 
            "导出当前周课表",
            "导出指定周次课表"
        ])
        layout.addWidget(self.share_combo)
        
        # 导出按钮
        self.export_btn = QPushButton("导出")
        self.export_btn.clicked.connect(self.export_schedule)
        layout.addWidget(self.export_btn)
        
    def export_schedule(self):
        """导出课表"""
        export_type = self.share_combo.currentText()
        
        # 生成默认文件名
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if export_type == "导出当前周课表":
            # 获取主窗口的当前周次
            main_window = self.parent()
            current_week = main_window.current_week if hasattr(main_window, 'current_week') else 1
            default_filename = f"课表_第{current_week}周_{current_time}.json"
            courses = self.get_current_week_courses(current_week)
        elif export_type == "导出指定周次课表":
            # TODO: 添加周次选择对话框
            weeks = self.select_weeks()
            if not weeks:
                return
            default_filename = f"课表_第{'-'.join(map(str, weeks))}周_{current_time}.json"
            courses = self.get_weeks_courses(weeks)
        else:  # 导出全部课表
            default_filename = f"课表_全部_{current_time}.json"
            courses = self.course_manager.get_courses()
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出课表",
            default_filename,
            "课表文件 (*.json)"
        )
        
        if file_path:
            try:
                self.save_courses_to_file(courses, file_path)
                QMessageBox.information(
                    self,
                    "导出成功",
                    f"课表已成功导出到：\n{file_path}"
                )
                # 在访达中显示文件
                os.system(f'open -R "{file_path}"')
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "导出失败",
                    f"导出课表时发生错误：\n{str(e)}"
                )
    
    def get_current_week_courses(self, week: int) -> list:
        """获取当前周的课程"""
        return [course for course in self.course_manager.get_courses()
                if week in self._parse_weeks(course.weeks)]
    
    def get_weeks_courses(self, weeks: list) -> list:
        """获取指定周次的课程"""
        return [course for course in self.course_manager.get_courses()
                if any(week in self._parse_weeks(course.weeks) for week in weeks)]
    
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
    
    def select_weeks(self) -> list:
        """选择周次对话框"""
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(
            self,
            "选择周次",
            "请输入要导出的周次（如：1-16 或 1,3,5-7）："
        )
        if ok and text:
            try:
                weeks = []
                for part in text.split(','):
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        weeks.extend(range(start, end + 1))
                    else:
                        weeks.append(int(part))
                return sorted(set(weeks))  # 去重并排序
            except:
                QMessageBox.warning(self, "输入错误", "请输入正确的周次格式！")
        return []
    
    def save_courses_to_file(self, courses: list, file_path: str):
        """保存课程到文件"""
        data = []
        for course in courses:
            data.append({
                'name': course.name,
                'room': course.room,
                'teacher': course.teacher,
                'weeks': course.weeks,
                'day_of_week': course.day_of_week,
                'start_time': course.start_time.strftime('%H:%M'),
                'end_time': course.end_time.strftime('%H:%M'),
                'description': course.description,
                'score': course.score
            })
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                'version': '1.0',
                'export_time': datetime.now().isoformat(),
                'courses': data
            }, f, ensure_ascii=False, indent=2)
