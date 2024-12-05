from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                            QTimeEdit, QSpinBox, QDialogButtonBox, QComboBox,
                            QTextEdit, QSlider, QLabel, QHBoxLayout)
from PyQt6.QtCore import Qt
from datetime import datetime, time
from models.course import Course

class CourseDialog(QDialog):
    """课程编辑对话框"""
    def __init__(self, parent=None, course: Course = None, preset_time: dict = None):
        super().__init__(parent)
        self.course = course
        self.preset_time = preset_time
        
        # 设置固定大小
        self.setFixedSize(400, 500)
        
        # 设置窗口位置到父窗口中央
        if parent:
            parent_center = parent.geometry().center()
            self.setGeometry(
                parent_center.x() - 200,
                parent_center.y() - 250,
                400,
                500
            )
        
        # 添加时间槽定义
        self.time_slots = [
            ("08:20", "09:55"),  # 第1-2节
            ("10:15", "11:50"),  # 第3-4节
            ("14:00", "15:35"),  # 第5-6节
            ("15:55", "17:30"),  # 第7-8节
            ("19:00", "20:35"),  # 晚上
        ]
        self.setup_ui()
        
        if course:
            self.load_course(course)
        elif preset_time:
            self.load_preset_time()
    
    def setup_ui(self):
        self.setWindowTitle("编辑课程" if self.course else "添加课程")
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        # 课程名称
        self.name_edit = QLineEdit()
        form.addRow("课程名称:", self.name_edit)
        
        # 教室
        self.room_edit = QLineEdit()
        form.addRow("教室:", self.room_edit)
        
        # 教师
        self.teacher_edit = QLineEdit()
        form.addRow("教师:", self.teacher_edit)
        
        # 周次滑块
        week_layout = QHBoxLayout()
        self.week_start_slider = QSlider(Qt.Orientation.Horizontal)
        self.week_start_slider.setRange(1, 20)
        self.week_start_slider.setValue(1)
        self.week_start_label = QLabel("1")
        
        self.week_end_slider = QSlider(Qt.Orientation.Horizontal)
        self.week_end_slider.setRange(1, 20)
        self.week_end_slider.setValue(16)
        self.week_end_label = QLabel("16")
        
        week_layout.addWidget(QLabel("从第"))
        week_layout.addWidget(self.week_start_slider)
        week_layout.addWidget(self.week_start_label)
        week_layout.addWidget(QLabel("周 到 第"))
        week_layout.addWidget(self.week_end_slider)
        week_layout.addWidget(self.week_end_label)
        week_layout.addWidget(QLabel("周"))
        
        form.addRow("周次:", week_layout)
        
        # 星期
        self.day_combo = QComboBox()
        self.day_combo.addItems(["周一", "周二", "周三", "周四", "周五", "周六", "周日"])
        form.addRow("星期:", self.day_combo)
        
        # 时间段滑块
        time_layout = QHBoxLayout()
        self.time_slot_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slot_slider.setRange(0, len(self.time_slots) - 1)
        self.time_slot_slider.setValue(0)
        self.time_slot_label = QLabel(self._get_time_slot_text(0))
        
        time_layout.addWidget(self.time_slot_slider)
        time_layout.addWidget(self.time_slot_label)
        
        form.addRow("时间段:", time_layout)
        
        # 描述
        self.desc_edit = QTextEdit()
        form.addRow("描述:", self.desc_edit)
        
        layout.addLayout(form)
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # 连接信号
        self.week_start_slider.valueChanged.connect(
            lambda v: self.week_start_label.setText(str(v))
        )
        self.week_end_slider.valueChanged.connect(
            lambda v: self.week_end_label.setText(str(v))
        )
        self.time_slot_slider.valueChanged.connect(
            lambda v: self.time_slot_label.setText(self._get_time_slot_text(v))
        )
        
        # 添加验证
        self.week_start_slider.valueChanged.connect(self._validate_week_range)
        self.week_end_slider.valueChanged.connect(self._validate_week_range)
    
    def _validate_week_range(self):
        """验证周次范围"""
        start = self.week_start_slider.value()
        end = self.week_end_slider.value()
        if start > end:
            if self.sender() == self.week_start_slider:
                self.week_end_slider.setValue(start)
            else:
                self.week_start_slider.setValue(end)
    
    def _get_time_slot_text(self, index: int) -> str:
        """获取时间段文本"""
        start, end = self.time_slots[index]
        slot_names = ["第1-2节", "第3-4节", "第5-6节", "第7-8节", "晚上"]
        return f"{slot_names[index]} ({start}-{end})"
    
    def get_course_data(self) -> Course:
        """获取表单数据"""
        time_slot_index = self.time_slot_slider.value()
        start_time, end_time = self.time_slots[time_slot_index]
        
        return Course(
            id=-1,  # 新课程的ID由数据库生成
            name=self.name_edit.text(),
            room=self.room_edit.text(),
            teacher=self.teacher_edit.text(),
            weeks=f"{self.week_start_slider.value()}-{self.week_end_slider.value()}周",
            day_of_week=self.day_combo.currentIndex() + 1,
            start_time=datetime.strptime(start_time, '%H:%M').time(),
            end_time=datetime.strptime(end_time, '%H:%M').time(),
            description=self.desc_edit.toPlainText()
        )
    
    def load_course(self, course: Course):
        """加载课程数据"""
        self.name_edit.setText(course.name)
        self.room_edit.setText(course.room)
        self.teacher_edit.setText(course.teacher)
        
        # 解析周次
        if '-' in course.weeks:
            start, end = course.weeks.replace('周', '').split('-')
            self.week_start_slider.setValue(int(start))
            self.week_end_slider.setValue(int(end))
        
        self.day_combo.setCurrentIndex(course.day_of_week - 1)
        
        # 设置时间段
        for i, (start, end) in enumerate(self.time_slots):
            if (datetime.strptime(start, '%H:%M').time() == course.start_time and
                datetime.strptime(end, '%H:%M').time() == course.end_time):
                self.time_slot_slider.setValue(i)
                break
        
        self.desc_edit.setText(course.description)
    
    def load_preset_time(self):
        """加载预设的时间信息"""
        if 'day_of_week' in self.preset_time:
            self.day_combo.setCurrentIndex(self.preset_time['day_of_week'] - 1)
            
        if 'start_time' in self.preset_time and 'end_time' in self.preset_time:
            # 根据预设时间找到对应的时间槽
            preset_start = self.preset_time['start_time']
            preset_end = self.preset_time['end_time']
            
            for i, (start, end) in enumerate(self.time_slots):
                if start == preset_start and end == preset_end:
                    self.time_slot_slider.setValue(i)
                    break
