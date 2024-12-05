from dataclasses import dataclass
from datetime import datetime, time
from typing import List, Optional

@dataclass
class Course:
    """课程数据模型"""
    id: int
    name: str                # 课程名称
    room: str               # 教室
    teacher: str            # 教师
    weeks: str             # 周次
    day_of_week: int       # 星期几(1-7)
    start_time: time       # 开始时间
    end_time: time         # 结束时间
    description: str = ""   # 课程描述
    score: float = 0.0     # 课程评分
    feedback: List[str] = None  # 课程反馈
    color: str = "#e3f2fd"  # 课程卡片颜色

    def conflicts_with(self, other: 'Course') -> bool:
        """检查是否与其他课程时间冲突"""
        if self.day_of_week != other.day_of_week:
            return False
            
        # 检查周次是否重叠
        self_weeks = self._parse_weeks(self.weeks)
        other_weeks = self._parse_weeks(other.weeks)
        if not set(self_weeks).intersection(set(other_weeks)):
            return False
            
        # 检查时间是否重叠
        return not (self.end_time <= other.start_time or 
                   self.start_time >= other.end_time)
    
    @staticmethod
    def _parse_weeks(weeks_str: str) -> List[int]:
        """解析周次字符串，如 "1-16周" -> [1,2,3,...,16]"""
        result = []
        for part in weeks_str.replace('周', '').split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                result.extend(range(start, end + 1))
            else:
                result.append(int(part))
        return result 