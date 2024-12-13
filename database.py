import json
import os
from typing import List, Optional
from models import Course
import sqlite3

class Database:
    def __init__(self, filename: str = 'courses.json'):
        self.filename = filename
        self.courses: List[Course] = []
        self.load_data()

    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.courses = [Course.from_dict(course_data) for course_data in data]

    def save_data(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump([course.to_dict() for course in self.courses], f, ensure_ascii=False, indent=2)

    def add_course(self, course: Course) -> bool:
        # Check for time conflicts
        for existing_course in self.courses:
            if existing_course.has_time_conflict(course):
                return False
        self.courses.append(course)
        self.save_data()
        return True

    def remove_course(self, course: Course):
        self.courses.remove(course)
        self.save_data()

    def update_course(self, old_course: Course, new_course: Course) -> bool:
        # Check for time conflicts with other courses
        for course in self.courses:
            if course != old_course and course.has_time_conflict(new_course):
                return False
        
        index = self.courses.index(old_course)
        self.courses[index] = new_course
        self.save_data()
        return True

    def get_courses_by_day(self, weekday: int) -> List[Course]:
        return [course for course in self.courses if course.weekday == weekday]

    def search_courses(self, query: str) -> List[Course]:
        query = query.lower()
        return [
            course for course in self.courses
            if query in course.name.lower() or
               query in course.teacher.lower() or
               query in course.location.lower() or
               (course.description and query in course.description.lower())
        ]

    def add_feedback(self, course: Course, feedback: str):
        if course.feedback is None:
            course.feedback = []
        course.feedback.append(feedback)
        self.save_data()

    def set_rating(self, course: Course, rating: float):
        course.rating = rating
        self.save_data()

    def get_course_score(self, course_id: int) -> Optional[float]:
        """获取课程评分"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT score FROM courses WHERE id = ?",
                (course_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else None
