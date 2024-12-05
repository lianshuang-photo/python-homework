from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional, List
import json

@dataclass
class Course:
    name: str
    teacher: str
    location: str
    start_time: time
    end_time: time
    weekday: int  # 0-6 representing Monday to Sunday
    description: Optional[str] = None
    rating: Optional[float] = None
    feedback: List[str] = None

    def to_dict(self):
        return {
            'name': self.name,
            'teacher': self.teacher,
            'location': self.location,
            'start_time': self.start_time.strftime('%H:%M'),
            'end_time': self.end_time.strftime('%H:%M'),
            'weekday': self.weekday,
            'description': self.description,
            'rating': self.rating,
            'feedback': self.feedback or []
        }

    @classmethod
    def from_dict(cls, data):
        data['start_time'] = datetime.strptime(data['start_time'], '%H:%M').time()
        data['end_time'] = datetime.strptime(data['end_time'], '%H:%M').time()
        return cls(**data)

    def has_time_conflict(self, other: 'Course') -> bool:
        if self.weekday != other.weekday:
            return False
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)
