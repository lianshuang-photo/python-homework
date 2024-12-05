from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QLineEdit, QLabel, QFrame, QMessageBox, QMenu, QFileDialog, QMenuBar, QDialog, QComboBox, QHeaderView,
                             QApplication, QStackedWidget)
from PyQt6.QtCore import Qt, QTimer, QRect, QPoint
from PyQt6.QtGui import (QColor, QFont, QIcon, QAction, QPainter, QPdfWriter,
                        QPixmap, QRegion, QPageSize, QKeySequence, QShortcut)
from datetime import datetime
from typing import List, Optional
import os
from .course_dialog import CourseDialog
from models.course_manager import CourseManager
from models.course import Course
from .feedback_dialog import FeedbackDialog
from .reminder_settings import ReminderSettings
from .statistics_dialog import StatisticsDialog
import json
from utils.theme_manager import ThemeManager
from ui.theme_dialog import ThemeDialog
from ui.sync_dialog import SyncDialog
from ui.share_dialog import ShareDialog
from ui.guide_dialog import GuideDialog
from .calendar_view import CalendarView

class CourseCard(QFrame):
    """课程卡片组件"""
    def __init__(self, course, parent=None):
        super().__init__(parent)
        self.course = course
        self.setObjectName("courseCard")
        self.setup_ui()
        
        # 添加详细的工具提示
        tooltip = (
            f"<html>"
            f"<h3>{course.name}</h3>"
            f"<p><b>教室：</b>{course.room}</p>"
            f"<p><b>教师：</b>{course.teacher}</p>"
            f"<p><b>时间：</b>{course.start_time.strftime('%H:%M')}-{course.end_time.strftime('%H:%M')}</p>"
            f"<p><b>周次：</b>{course.weeks}</p>"
            f"<p><b>描述：</b>{course.description}</p>"
            f"</html>"
        )
        self.setToolTip(tooltip)
        
        # 启用鼠标追踪
        self.setMouseTracking(True)
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # 课程名称
        name_label = QLabel(self.course.name)
        name_label.setObjectName("courseName")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        # 教室信息
        if self.course.room:
            room_label = QLabel(f"📍 {self.course.room}")
            room_label.setObjectName("infoText")
            layout.addWidget(room_label)
        
        # 教师信息
        if self.course.teacher:
            teacher_label = QLabel(f"👤 {self.course.teacher}")
            teacher_label.setObjectName("infoText")
            layout.addWidget(teacher_label)
        
        # 周次信息 - 总课表视图中显示
        week_label = QLabel(f"🗓️ {self.course.weeks}")
        week_label.setObjectName("infoText")
        layout.addWidget(week_label)
        
        layout.addStretch()
        
        # 设置基本样式
        self.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #e2e2e2;  # 使用边框替代阴影
                border-radius: 6px;
            }
        """)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.pos())
            
    def show_context_menu(self, pos):
        menu = QMenu(self)
        
        edit_action = QAction("编辑", self)
        edit_action.triggered.connect(self.edit_course)
        menu.addAction(edit_action)
        
        feedback_action = QAction("评分反馈", self)
        feedback_action.triggered.connect(self.show_feedback)
        menu.addAction(feedback_action)
        
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(self.delete_course)
        menu.addAction(delete_action)
        
        menu.exec(self.mapToGlobal(pos))
        
    def edit_course(self):
        dialog = CourseDialog(self.parent(), self.course)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 获取父窗口（MainWindow）并更新课程
            main_window = self.window()
            if hasattr(main_window, 'update_course'):
                main_window.update_course(self.course.id, dialog.get_course_data())
                
    def delete_course(self):
        reply = QMessageBox.question(
            self, '确删除',
            f'确定要删除课程 "{self.course.name}" 吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            main_window = self.window()
            if hasattr(main_window, 'delete_course'):
                main_window.delete_course(self.course.id)

    def show_feedback(self):
        """显示评分对话框"""
        dialog = FeedbackDialog(self.course, self.window())
        dialog.exec()

    def enterEvent(self, event):
        """鼠标进入事件"""
        self.setStyleSheet("""
            QFrame {
                background-color: #e8f0fe;
                border-radius: 6px;
            }
        """)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """鼠标离开事件"""
        self.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 6px;
            }
        """)
        super().leaveEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            self.course_manager = CourseManager()
            self.current_week = 1  # 当前周次
            self.theme_manager = ThemeManager()
            
            # 随机选择一个主题
            import random
            available_themes = list(ThemeManager.THEMES.keys())
            random_theme = random.choice(available_themes)
            self.theme_manager.set_theme(random_theme)
            
            self.setup_ui()
            
            # 只使用主题管理器的样式表
            self.setStyleSheet(self.theme_manager.get_stylesheet())
            
            self.load_courses()
            self.setup_timer()
            self.connect_signals()
            self.setup_shortcuts()  # 设置快捷键
        except Exception as e:
            QMessageBox.critical(self, "初始化错误", f"窗口初始化失败：{str(e)}")

    def setup_timer(self):
        """设置定时器用于课程提醒"""
        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self.check_course_reminders)
        self.reminder_timer.start(60000)  # 每分钟检查一次
        
        # 加载提醒设置
        self.load_reminder_settings()
        
    def load_reminder_settings(self):
        """加载提醒设置"""
        try:
            with open('settings.json', 'r') as f:
                self.reminder_settings = json.load(f)
        except:
            self.reminder_settings = {
                'reminder_time': 15,
                'sound_type': '默认'
            }
        
    def check_course_reminders(self):
        """检查是否需要发送课程提醒"""
        current_time = datetime.now().time()
        current_weekday = datetime.now().weekday() + 1
        
        for course in self.course_manager.get_courses(self.current_week):
            if course.day_of_week == current_weekday:
                # 计算提醒时间（课程开始前15分钟）
                reminder_minutes = course.start_time.hour * 60 + course.start_time.minute - 15
                if reminder_minutes < 0:
                    reminder_minutes = 0
                    
                reminder_hour = reminder_minutes // 60
                reminder_minute = reminder_minutes % 60
                reminder_time = datetime.strptime(f"{reminder_hour:02d}:{reminder_minute:02d}", "%H:%M").time()
                
                if current_time.hour == reminder_time.hour and \
                   current_time.minute == reminder_time.minute:
                    self.show_course_reminder(course)
                    
    def show_course_reminder(self, course):
        """显示课程提醒"""
        QMessageBox.information(
            self,
            "课程提",
            f"课程 {course.name} 将在15分钟后开始\n"
            f"教室: {course.room}\n"
            f"教师: {course.teacher}"
        )

    def check_course_conflicts(self, course: Course) -> List[Course]:
        """检查课程冲突并返回冲突的课程列表"""
        conflicts = []
        existing_courses = self.course_manager.get_courses()
        for existing_course in existing_courses:
            if course.id != existing_course.id and course.conflicts_with(existing_course):
                conflicts.append(existing_course)
        return conflicts

    def show_conflict_warning(self, conflicts: List[Course]):
        """显示课程冲突警"""
        conflict_msg = "以下课程时间在冲突：\n\n"
        for course in conflicts:
            conflict_msg += f"- {course.name} ({course.weeks} {course.start_time}-{course.end_time})\n"
        conflict_msg += "\n是否继续添加？"
        
        reply = QMessageBox.warning(
            self,
            "课程时间冲突",
            conflict_msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes

    def add_course(self):
        """添加新课程"""
        dialog = CourseDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            course = dialog.get_course_data()
            conflicts = self.check_course_conflicts(course)
            
            if conflicts and not self.show_conflict_warning(conflicts):
                return
            
            if self.course_manager.add_course(course):
                self.load_courses()
            else:
                QMessageBox.critical(
                    self,
                    "添加失败",
                    "添加课程时发生错误"
                )

    def update_course(self, course_id: int, new_course_data: Course):
        """更新课程信息"""
        if self.course_manager.update_course(course_id, new_course_data):
            self.load_courses()
        else:
            QMessageBox.warning(
                self,
                "新失败",
                "课程时间存在冲突，请选择其他时间"
            )

    def delete_course(self, course_id: int):
        """删除课程"""
        if self.course_manager.delete_course(course_id):
            self.load_courses()
        else:
            QMessageBox.warning(
                self,
                "删除失败",
                "删除课程时发生错误"
            )

    def load_courses(self):
        """加载课程数据到表格"""
        # 清空现有课程
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                self.table.setCellWidget(row, col, None)
        
        # 加载课程
        courses = self.course_manager.get_courses()
        for course in courses:
            # 如果是总课表或者课程在当前周进行，则显示
            if self.current_week == 0 or self.current_week in self._parse_weeks(course.weeks):
                row = self._get_time_slot_index(course.start_time)
                col = course.day_of_week - 1
                if row is not None:
                    self.table.setCellWidget(row, col, CourseCard(course))

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

    def _get_time_slot_index(self, time) -> Optional[int]:
        """根据时间获取对应时间段索引"""
        time_slots = [
            ("08:20", "09:55"),  # 第1-2节
            ("10:15", "11:50"),  # 第3-4节
            ("14:00", "15:35"),  # 第5-6节
            ("15:55", "17:30"),  # 第7-8节
            ("19:00", "20:35"),  # 晚上
        ]
        
        time_str = time.strftime("%H:%M")
        for i, (start, end) in enumerate(time_slots):
            if start <= time_str <= end:
                return i
        return None

    def export_schedule(self):
        """导出课表"""
        # 生成默认文件名：课表_周次_日期时间
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        week_text = "总课表" if self.current_week == 0 else f"第{self.current_week}周"
        default_filename = f"课表_{week_text}_{current_time}"
        
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)  # 设置为保存模式
        
        # 设置文件类型过滤器
        filters = {
            "PDF文件 (*.pdf)": ".pdf",
            "PNG图片 (*.png)": ".png"
        }
        dialog.setNameFilters(list(filters.keys()))
        
        # 设置默认文件名（不带扩展名）
        dialog.selectFile(default_filename)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                # 获取选择的文件类型和路径
                selected_filter = dialog.selectedNameFilter()
                file_path = dialog.selectedFiles()[0]
                extension = filters[selected_filter]
                
                # 确保文件有正确的扩展名
                if not file_path.endswith(extension):
                    file_path += extension
                
                # 根据文件类型导出
                if extension == '.pdf':
                    self.export_to_pdf(file_path)
                else:
                    self.export_to_image(file_path)
                
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
                    f"导出课表发生错误：\n{str(e)}"
                )

    def export_to_pdf(self, file_path: str):
        """导出为PDF"""
        # 创建PDF写入器
        writer = QPdfWriter(file_path)
        writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        writer.setResolution(300)  # 设置高分辨率
        
        # 计算页面大小和边距
        page_width = writer.width()
        page_height = writer.height()
        margin = int(writer.resolution() * 0.4)  # 1cm边距
        
        # 创建绘图器
        painter = QPainter()
        painter.begin(writer)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 抗锯齿
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)  # 文字抗锯齿
        
        # 使用系统默认字体
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        painter.setFont(font)
        
        # 绘制标题
        week_text = "总课表" if self.current_week == 0 else f"第{self.current_week}周课表"
        title_text = f"课程表 - {week_text}"
        
        # 绘制标题
        title_rect = QRect(margin, margin, page_width - 2 * margin, margin)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, title_text)
        
        # 计算表格区域
        content_rect = QRect(
            margin,
            margin * 2,  # 标题下
            page_width - 2 * margin,
            page_height - 3 * margin
        )
        
        # 保存当前状态
        painter.save()
        
        # 移动到内容区域并缩放
        painter.translate(content_rect.topLeft())
        scale = min(
            content_rect.width() / self.table.width(),
            content_rect.height() / self.table.height()
        )
        painter.scale(scale, scale)
        
        # 只渲染表格部分
        self.table.render(painter)
        
        # 恢复状态
        painter.restore()
        painter.end()

    def export_to_image(self, file_path: str):
        """导出为高清PNG图片"""
        # 获取表格尺寸
        table_width = self.table.horizontalHeader().length() + self.table.verticalHeader().width()
        table_height = self.table.verticalHeader().length() + self.table.horizontalHeader().height()
        
        # 设置2倍分辨率
        scale_factor = 2.0
        title_height = 60 * scale_factor
        
        # 创建高分辨率图片
        image = QPixmap(int(table_width * scale_factor), int(table_height * scale_factor + title_height))
        image.fill(Qt.GlobalColor.white)
        
        # 创建绘图器
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # 使用系统默认字体
        font = QFont()
        font.setPointSize(int(16 * scale_factor))
        font.setBold(True)
        painter.setFont(font)
        
        # 绘制标题
        week_text = "总课表" if self.current_week == 0 else f"第{self.current_week}周课表"
        title_text = f"课程表 - {week_text}"
        
        title_rect = QRect(0, 0, int(table_width * scale_factor), int(title_height))
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, title_text)
        
        # 绘制表格
        painter.translate(0, title_height)
        painter.scale(scale_factor, scale_factor)
        
        # 设置裁剪区域以确保不会绘制到边界外
        painter.setClipRect(0, 0, table_width, table_height)
        
        # 渲染表格
        self.table.render(painter)
        
        painter.end()
        
        # 保存高质量图片
        image.save(file_path, "PNG", quality=100)

    def connect_signals(self):
        """连接信号和槽"""
        # 删除原有的按钮连接
        # self.home_btn.clicked.connect(self.on_home_clicked)
        # self.table_btn.clicked.connect(self.on_table_clicked)
        
        # 新按钮的连接
        self.custom_btn.clicked.connect(self.on_custom_clicked)
        self.import_btn.clicked.connect(self.on_import_clicked)
        self.export_btn.clicked.connect(self.export_schedule)
        self.add_course_btn.clicked.connect(self.add_course)
        
        # 周次相关的连接
        self.week_combo.currentIndexChanged.connect(self.on_week_changed)
        self.prev_week_btn.clicked.connect(self.previous_week)
        self.next_week_btn.clicked.connect(self.next_week)

    def on_search(self, text: str):
        """搜索课程"""
        # 清空表格
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                widget = self.table.cellWidget(row, col)
                if widget:
                    if text.lower() in widget.course.name.lower() or \
                       text.lower() in widget.course.teacher.lower() or \
                       text.lower() in widget.course.room.lower() or \
                       text.lower() in widget.course.description.lower():
                        widget.setStyleSheet("""
                            QFrame {
                                background-color: #e3f2fd;
                                border: 2px solid #2196f3;
                                border-radius: 6px;
                            }
                        """)
                    else:
                        widget.setStyleSheet("""
                            QFrame {
                                background-color: #f8f9fa;
                                border-radius: 6px;
                            }
                        """)

    def on_import_clicked(self):
        """导入课表"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "导入课表",
            "",
            "课表文件 (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 检查文件格式
                if 'version' in data and 'courses' in data:
                    # 新版本格式
                    courses_data = data['courses']
                else:
                    # 旧版本格式（直接的课程列表）
                    courses_data = data
                
                # 清空现有课程
                self.course_manager.clear_courses()
                
                # 导入新课程
                for course_data in courses_data:
                    course = Course(
                        id=-1,  # 新课程的ID由数据库生成
                        name=course_data['name'],
                        room=course_data['room'],
                        teacher=course_data['teacher'],
                        weeks=course_data['weeks'],
                        day_of_week=course_data['day_of_week'],
                        start_time=datetime.strptime(course_data['start_time'], '%H:%M').time(),
                        end_time=datetime.strptime(course_data['end_time'], '%H:%M').time(),
                        description=course_data.get('description', ''),  # 使用get方法处理可选字段
                        score=course_data.get('score', 0)
                    )
                    self.course_manager.add_course(course)
                
                self.load_courses()
                QMessageBox.information(self, "导入成功", "课表导入成！")
                
            except Exception as e:
                QMessageBox.warning(self, "导入失败", f"导入课表时发生错误：{str(e)}")

    def on_custom_clicked(self):
        """显示主题设置对话框"""
        dialog = ThemeDialog(self)
        dialog.theme_changed.connect(self.change_theme)
        dialog.exec()

    def change_theme(self, theme_name: str):
        """切换主题"""
        self.theme_manager.set_theme(theme_name)
        self.setStyleSheet(self.theme_manager.get_stylesheet())

    def on_week_changed(self, index):
        """周次下拉框改变事件"""
        if index == 0:  # 总课表
            self.current_week = 0
            self.prev_week_btn.setEnabled(False)
            self.next_week_btn.setEnabled(False)
        else:
            self.current_week = index
            self.update_week_nav_buttons()
        self.load_courses()

    def update_week_nav_buttons(self):
        """更新周次导航按钮状态"""
        self.prev_week_btn.setEnabled(self.current_week > 1)
        self.next_week_btn.setEnabled(self.current_week < 20)

    def previous_week(self):
        """切换到上一周"""
        if self.current_week > 1:
            self.current_week -= 1
            self.week_combo.setCurrentIndex(self.current_week - 1)
            self.load_courses()

    def next_week(self):
        """切换到下一周"""
        if self.current_week < 20:
            self.current_week += 1
            self.week_combo.setCurrentIndex(self.current_week - 1)
            self.load_courses()

    def setup_ui(self):
        self.setWindowTitle("课表管理系统")
        self.setMinimumSize(1200, 800)
        
        # 设置窗口位置到屏幕中央偏上位置
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(
            (screen.width() - 1200) // 2,
            (screen.height() - 800) // 3,  # 向上偏移，避免被 Dock 遮挡
            1200,
            800
        )
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 建菜单栏
        self.setup_menu()

        # 顶部工具栏
        toolbar = QWidget()
        toolbar.setObjectName("toolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 16)
        toolbar_layout.setSpacing(20)
        
        # 左侧按钮组
        left_buttons = QWidget()
        left_layout = QHBoxLayout(left_buttons)
        left_layout.setSpacing(12)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.sync_btn = QPushButton("同步日历")
        self.sync_btn.setIcon(QIcon("ui/icons/sync.png"))
        
        self.share_btn = QPushButton("分享课表")
        self.share_btn.setIcon(QIcon("ui/icons/share.png"))
        
        self.custom_btn = QPushButton("自定义主题")
        
        left_layout.addWidget(self.sync_btn)
        left_layout.addWidget(self.share_btn)
        left_layout.addWidget(self.custom_btn)
        
        # 连接信号
        self.sync_btn.clicked.connect(self.show_sync_dialog)
        self.share_btn.clicked.connect(self.show_share_dialog)
        
        # 周次选择控件
        week_widget = QWidget()
        week_widget.setObjectName("weekSelector")
        week_layout = QHBoxLayout(week_widget)
        week_layout.setContentsMargins(8, 0, 8, 0)
        week_layout.setSpacing(8)
        
        # 左箭头按钮
        self.prev_week_btn = QPushButton("◀")
        self.prev_week_btn.setObjectName("weekNavBtn")
        
        # 周次下拉框
        self.week_combo = QComboBox()
        self.week_combo.setObjectName("weekCombo")
        self.week_combo.addItem("总课表")
        for i in range(1, 21):
            self.week_combo.addItem(f"第{i}周")
        self.week_combo.setCurrentIndex(self.current_week)
        
        # 右箭头按钮
        self.next_week_btn = QPushButton("▶")
        self.next_week_btn.setObjectName("weekNavBtn")
        
        week_layout.addWidget(self.prev_week_btn)
        week_layout.addWidget(self.week_combo)
        week_layout.addWidget(self.next_week_btn)
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索课程...")
        self.search_input.setMinimumWidth(240)
        self.search_input.setMaximumWidth(400)
        self.search_input.textChanged.connect(self.on_search)  # 添加搜索信号连接
        
        # 右侧按钮组
        right_buttons = QWidget()
        right_layout = QHBoxLayout(right_buttons)
        right_layout.setSpacing(12)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.import_btn = QPushButton("导入课表")
        self.export_btn = QPushButton("导出课表")
        self.add_course_btn = QPushButton("添加课程")
        self.add_course_btn.setObjectName("addCourseBtn")
        
        right_layout.addWidget(self.import_btn)
        right_layout.addWidget(self.export_btn)
        right_layout.addWidget(self.add_course_btn)
        
        # 组装工具栏
        toolbar_layout.addWidget(left_buttons)
        toolbar_layout.addWidget(week_widget)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(right_buttons)
        
        main_layout.addWidget(toolbar)

        # 课程表
        self.table = CustomTableWidget()
        self.setup_table()
        main_layout.addWidget(self.table)

        # 添加视图切换按钮
        view_buttons = QWidget()
        view_layout = QHBoxLayout(view_buttons)
        
        self.table_view_btn = QPushButton("表格视图")
        self.calendar_view_btn = QPushButton("日历视图")
        
        view_layout.addWidget(self.table_view_btn)
        view_layout.addWidget(self.calendar_view_btn)
        
        # 创建视图容器
        self.view_stack = QStackedWidget()
        self.table_view = self.table  # 原有的表格视图
        self.calendar_view = CalendarView(self.course_manager)
        
        self.view_stack.addWidget(self.table_view)
        self.view_stack.addWidget(self.calendar_view)
        
        # 连接信号
        self.table_view_btn.clicked.connect(lambda: self.view_stack.setCurrentWidget(self.table_view))
        self.calendar_view_btn.clicked.connect(lambda: self.view_stack.setCurrentWidget(self.calendar_view))
        
        # 更新布局
        toolbar_layout.addWidget(view_buttons)
        main_layout.addWidget(self.view_stack)

    def setup_menu(self):
        """设置菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        import_action = QAction("导入课表", self)
        import_action.triggered.connect(self.on_import_clicked)
        file_menu.addAction(import_action)
        
        export_action = QAction("导出课表", self)
        export_action.triggered.connect(self.export_schedule)
        file_menu.addAction(export_action)
        
        # 设置菜单
        settings_menu = menubar.addMenu("设置")
        
        reminder_action = QAction("提醒设置", self)
        reminder_action.triggered.connect(self.show_reminder_settings)
        settings_menu.addAction(reminder_action)
        
        theme_action = QAction("主题设置", self)
        theme_action.triggered.connect(self.on_custom_clicked)
        settings_menu.addAction(theme_action)
        
        # 添加统计菜单
        stats_menu = menubar.addMenu("统计")
        
        course_stats_action = QAction("课程统计", self)
        course_stats_action.triggered.connect(self.show_statistics)
        stats_menu.addAction(course_stats_action)
        
        # 添加帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        guide_action = QAction("使用指南", self)
        guide_action.triggered.connect(self.show_guide)
        help_menu.addAction(guide_action)
        
        # 添加数据管理菜单
        data_menu = menubar.addMenu("数据")
        
        backup_action = QAction("创建备份", self)
        backup_action.triggered.connect(self.create_backup)
        data_menu.addAction(backup_action)
        
        restore_action = QAction("恢复备份", self)
        restore_action.triggered.connect(self.restore_backup)
        data_menu.addAction(restore_action)

    def show_reminder_settings(self):
        """显示提醒设置对话框"""
        dialog = ReminderSettings(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            dialog.save_settings()
            # 更新提醒设置

    def show_statistics(self):
        """显示统计对话框"""
        dialog = StatisticsDialog(self.course_manager, self)
        dialog.exec()

    def setup_table(self):
        """初始化课程表格"""
        self.table = CustomTableWidget()
        self.table.setColumnCount(7)  # 周一到周日
        self.table.setRowCount(5)     # 5个时间段
        
        # 设置表头
        headers = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        self.table.setHorizontalHeaderLabels(headers)
        
        # 设置左侧时间签
        time_slots = [
            "第1-2节\n08:20-09:55",
            "第3-4节\n10:15-11:50",
            "第5-6节\n14:00-15:35",
            "第7-8节\n15:55-17:30",
            "晚上\n19:00-20:35"
        ]
        self.table.setVerticalHeaderLabels(time_slots)
        
        # 设置单元格大小
        for i in range(self.table.rowCount()):
            self.table.setRowHeight(i, 130)  # 稍微小行高
        
        # 动态设置列宽，确保显示所有列
        viewport_width = self.table.viewport().width()
        header_width = 100  # 垂直表头宽度
        available_width = viewport_width - header_width
        column_width = available_width // 7  # 平均分配宽度给7列
        
        for i in range(self.table.columnCount()):
            self.table.setColumnWidth(i, column_width)
        
        # 设置表头属性
        header = self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFixedHeight(40)  # 减小表头高度
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # 自动拉伸列宽
        
        v_header = self.table.verticalHeader()
        v_header.setDefaultAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        v_header.setFixedWidth(100)  # 减小垂直表头宽度
        
        # 启用双击事件
        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        
        # 启用鼠标追踪
        self.table.setMouseTracking(True)
        # 使用 cellEntered 信号
        self.table.cellEntered.connect(self.on_cell_entered)
        # 创建一个变量来跟踪上一个高亮的单元格
        self.last_highlighted_cell = None

    def on_cell_double_clicked(self, row: int, column: int):
        """处理单元格双击事件"""
        # 检单元格是否已有课程
        if self.table.cellWidget(row, column) is not None:
            return
        
        # 获取对应的时间段
        time_slots = [
            ("08:20", "09:55"),  # 第1-2节
            ("10:15", "11:50"),  # 第3-4节
            ("14:00", "15:35"),  # 第5-6节
            ("15:55", "17:30"),  # 第7-8节
            ("19:00", "20:35"),  # 晚上
        ]
        
        if 0 <= row < len(time_slots):
            start_time, end_time = time_slots[row]
            day_of_week = column + 1  # 转换为星期几（1-7）
            
            # 打开添加课程对话框并预填充时间信息
            dialog = CourseDialog(self, preset_time={
                'day_of_week': day_of_week,
                'start_time': start_time,
                'end_time': end_time
            })
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                course = dialog.get_course_data()
                if self.course_manager.add_course(course):
                    self.load_courses()
                else:
                    QMessageBox.warning(
                        self,
                        "添加失败",
                        "课程时间存在冲突，请选择其他时间"
                    )

    def on_cell_entered(self, row: int, column: int):
        """鼠标进入单元格时的处理"""
        # 清除上一个高亮的单元格
        if self.last_highlighted_cell:
            last_row, last_col = self.last_highlighted_cell
            if self.table.cellWidget(last_row, last_col) is None:
                item = self.table.item(last_row, last_col)
                if item:
                    item.setBackground(QColor("#ffffff"))
        
        # 高亮当前单元格
        if self.table.cellWidget(row, column) is None:
            item = self.table.item(row, column)
            if not item:
                item = QTableWidgetItem()
                self.table.setItem(row, column, item)
            item.setBackground(QColor("#f8f9fa"))
            self.last_highlighted_cell = (row, column)

    def leaveEvent(self, event):
        """鼠标离开表格时的处理"""
        # 清除高亮
        if self.last_highlighted_cell:
            row, col = self.last_highlighted_cell
            if self.table.cellWidget(row, col) is None:
                item = self.table.item(row, col)
                if item:
                    item.setBackground(QColor("#ffffff"))
            self.last_highlighted_cell = None
        super().leaveEvent(event)

    def show_sync_dialog(self):
        """显示同步对话框"""
        dialog = SyncDialog(self.course_manager, self)
        dialog.exec()

    def show_share_dialog(self):
        """显示分享对话框"""
        dialog = ShareDialog(self.course_manager, self)
        dialog.exec()

    def setup_shortcuts(self):
        """设置快捷键"""
        # 添加课程 (Ctrl+N)
        add_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        add_shortcut.activated.connect(self.add_course)
        
        # 导出课表 (Ctrl+E)
        export_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        export_shortcut.activated.connect(self.export_schedule)
        
        # 导入课表 (Ctrl+I)
        import_shortcut = QShortcut(QKeySequence("Ctrl+I"), self)
        import_shortcut.activated.connect(self.on_import_clicked)
        
        # 搜索 (Ctrl+F)
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(lambda: self.search_input.setFocus())
        
        # 切换周次 (Alt+Left/Right)
        prev_week_shortcut = QShortcut(QKeySequence("Alt+Left"), self)
        prev_week_shortcut.activated.connect(self.previous_week)
        
        next_week_shortcut = QShortcut(QKeySequence("Alt+Right"), self)
        next_week_shortcut.activated.connect(self.next_week)

    def show_guide(self):
        """显示使用指南"""
        dialog = GuideDialog(self)
        dialog.exec()

    def create_backup(self):
        """创建数据备份"""
        try:
            backup_path = self.backup_manager.create_backup()
            QMessageBox.information(
                self,
                "备份成功",
                f"数据已备份到：\n{backup_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "备份失败",
                f"创建备份时发生错误：\n{str(e)}"
            )

    def restore_backup(self):
        """恢复数据备份"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择备份文件",
            "backups",
            "备份文件 (*.zip)"
        )
        
        if file_path:
            reply = QMessageBox.warning(
                self,
                "确认恢复",
                "恢复备份将覆盖当前数据，是否继续？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.backup_manager.restore_backup(file_path):
                    QMessageBox.information(
                        self,
                        "恢复成功",
                        "数据已恢复，程序将重启以应用更改。"
                    )
                    self.restart_application()
                else:
                    QMessageBox.critical(
                        self,
                        "恢复失败",
                        "恢复备份时发生错误"
                    )

    def restart_application(self):
        """重启应用程序"""
        import sys
        import os
        os.execl(sys.executable, sys.executable, *sys.argv)

# 添加自定义表格类
class CustomTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_highlighted_cell = None
        self.setMouseTracking(True)
        self.cellEntered.connect(self.on_cell_entered)

    def on_cell_entered(self, row: int, column: int):
        """鼠标进入单元格时的处理"""
        # 清除上一个高亮的单元格
        if self.last_highlighted_cell:
            last_row, last_col = self.last_highlighted_cell
            if self.cellWidget(last_row, last_col) is None:
                item = self.item(last_row, last_col)
                if item:
                    item.setBackground(QColor("#ffffff"))
        
        # 高亮当前单元格
        if self.cellWidget(row, column) is None:
            item = self.item(row, column)
            if not item:
                item = QTableWidgetItem()
                self.setItem(row, column, item)
            item.setBackground(QColor("#f8f9fa"))
            self.last_highlighted_cell = (row, column)

    def leaveEvent(self, event):
        """鼠标离开表格时的处理"""
        # 清除高亮
        if self.last_highlighted_cell:
            row, col = self.last_highlighted_cell
            if self.cellWidget(row, col) is None:
                item = self.item(row, col)
                if item:
                    item.setBackground(QColor("#ffffff"))
            self.last_highlighted_cell = None
        super().leaveEvent(event)
