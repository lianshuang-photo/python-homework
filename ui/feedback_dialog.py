from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTextEdit, QSlider)
from PyQt6.QtCore import Qt
from datetime import datetime

class FeedbackDialog(QDialog):
    """课程评分和反馈对话框"""
    def __init__(self, course, parent=None):
        super().__init__(parent)
        self.course = course
        self.setup_ui()
        self.load_feedback()
        
    def setup_ui(self):
        self.setWindowTitle(f"课程评价 - {self.course.name}")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        
        # 评分滑块
        score_layout = QHBoxLayout()
        score_label = QLabel("评分:")
        self.score_slider = QSlider(Qt.Orientation.Horizontal)
        self.score_slider.setRange(0, 50)  # 0-5分，精确到小数点后一位
        self.score_slider.setValue(int(self.course.score * 10))
        self.score_value = QLabel(f"{self.course.score:.1f}")
        self.score_slider.valueChanged.connect(
            lambda v: self.score_value.setText(f"{v/10:.1f}")
        )
        
        score_layout.addWidget(score_label)
        score_layout.addWidget(self.score_slider)
        score_layout.addWidget(self.score_value)
        layout.addLayout(score_layout)
        
        # 反馈输入框
        self.feedback_edit = QTextEdit()
        self.feedback_edit.setPlaceholderText("输入你的课程反馈...")
        layout.addWidget(self.feedback_edit)
        
        # 历史反馈
        self.feedback_list = QTextEdit()
        self.feedback_list.setReadOnly(True)
        layout.addWidget(self.feedback_list)
        
        # 按钮
        buttons_layout = QHBoxLayout()
        submit_btn = QPushButton("提交")
        submit_btn.clicked.connect(self.submit_feedback)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(submit_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
    def load_feedback(self):
        """加载历史反馈"""
        main_window = self.parent()
        if hasattr(main_window, 'course_manager'):
            # 获取评分和反馈
            feedback_list = main_window.course_manager.get_feedback(self.course.id)
            
            # 显示历史反馈
            feedback_text = ""
            for content, score, created_at in feedback_list:
                date = datetime.fromisoformat(created_at).strftime('%Y-%m-%d %H:%M')
                feedback_text += f"[{date}] 评分：{score:.1f}\n{content}\n\n"
            self.feedback_list.setText(feedback_text)
            
            # 如果有历史评分，显示最新的评分
            if feedback_list:
                latest_score = feedback_list[0][1]  # 最新的评分
                self.score_slider.setValue(int(latest_score * 10))
                self.score_value.setText(f"{latest_score:.1f}")
        
    def submit_feedback(self):
        """提交评分和反馈"""
        score = self.score_slider.value() / 10
        feedback = self.feedback_edit.toPlainText()
        
        if not feedback.strip():
            return
        
        main_window = self.parent()
        if hasattr(main_window, 'course_manager'):
            if main_window.course_manager.add_feedback(self.course.id, feedback, score):
                self.load_feedback()  # 重新加载显示最新反馈
                self.feedback_edit.clear()  # 清空输入框
