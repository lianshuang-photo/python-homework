import sqlite3
from typing import List, Optional
from .course import Course
from datetime import datetime, time

class CourseManager:
    """课程数据管理类"""
    def __init__(self, db_path: str = "courses.db"):
        self.db_path = db_path
        self._init_db()
        self._cache = {}  # 添加缓存
        
    def _init_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            # 创建临时表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id INTEGER,
                    content TEXT,
                    score REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (course_id) REFERENCES courses (id)
                )
            """)
            
            # 检查是否存在旧的feedback表
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='feedback'
            """)
            if cursor.fetchone():
                # 复制旧数据到新表
                conn.execute("""
                    INSERT INTO feedback_new (id, course_id, content, created_at)
                    SELECT id, course_id, content, created_at FROM feedback
                """)
                # 删除旧表
                conn.execute("DROP TABLE feedback")
            
            # 重命名新表
            conn.execute("ALTER TABLE feedback_new RENAME TO feedback")
            
            # 创建或更新courses表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    room TEXT,
                    teacher TEXT,
                    weeks TEXT,
                    day_of_week INTEGER,
                    start_time TEXT,
                    end_time TEXT,
                    description TEXT,
                    score REAL DEFAULT 0,
                    color TEXT
                )
            """)
    
    def add_course(self, course: Course) -> bool:
        """添加课程"""
        # 检查时间冲突
        if self._check_conflicts(course):
            return False
            
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO courses (name, room, teacher, weeks, day_of_week,
                                   start_time, end_time, description, color)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (course.name, course.room, course.teacher, course.weeks,
                 course.day_of_week, course.start_time.strftime('%H:%M'),
                 course.end_time.strftime('%H:%M'), course.description,
                 course.color))
        # 清除缓存
        self._clear_cache()
        return True
    
    def _parse_weeks(self, weeks_str: str) -> list:
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
    
    def get_courses(self, week: Optional[int] = None) -> List[Course]:
        """获取课程列表（添加缓存）"""
        cache_key = f"courses_week_{week}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM courses")
            courses = [self._row_to_course(row) for row in cursor.fetchall()]
            
            if week:
                courses = [c for c in courses if week in self._parse_weeks(c.weeks)]
            
            self._cache[cache_key] = courses
            return courses
    
    def _row_to_course(self, row: sqlite3.Row) -> Course:
        """将数据库行转换为Course对象"""
        return Course(
            id=row['id'],
            name=row['name'],
            room=row['room'],
            teacher=row['teacher'],
            weeks=row['weeks'],
            day_of_week=row['day_of_week'],
            start_time=datetime.strptime(row['start_time'], '%H:%M').time(),
            end_time=datetime.strptime(row['end_time'], '%H:%M').time(),
            description=row['description'],
            color=row['color']
        )
    
    def _check_conflicts(self, new_course: Course) -> bool:
        """检查是否存在时间冲突"""
        existing_courses = self.get_courses()
        return any(new_course.conflicts_with(course) for course in existing_courses) 
    
    def update_course(self, course_id: int, course: Course) -> bool:
        """更新课程信息"""
        # 检查时间冲突（排除当前课程）
        existing_courses = [c for c in self.get_courses() if c.id != course_id]
        if any(course.conflicts_with(c) for c in existing_courses):
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE courses 
                SET name=?, room=?, teacher=?, weeks=?, day_of_week=?,
                    start_time=?, end_time=?, description=?, color=?
                WHERE id=?
            """, (course.name, course.room, course.teacher, course.weeks,
                  course.day_of_week, course.start_time.strftime('%H:%M'),
                  course.end_time.strftime('%H:%M'), course.description,
                  course.color, course_id))
        # 清除缓存
        self._clear_cache()
        return True
    
    def delete_course(self, course_id: int) -> bool:
        """删除课程"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM courses WHERE id=?", (course_id,))
                conn.execute("DELETE FROM feedback WHERE course_id=?", (course_id,))
            # 清��缓存
            self._clear_cache()
            return True
        except sqlite3.Error:
            return False
    
    def search_courses(self, keyword: str) -> List[Course]:
        """搜索课程"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM courses 
                WHERE name LIKE ? OR teacher LIKE ? OR room LIKE ?
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
            return [self._row_to_course(row) for row in cursor.fetchall()]
    
    def add_feedback(self, course_id: int, content: str, score: float) -> bool:
        """添加课程反馈"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO feedback (course_id, content, score) VALUES (?, ?, ?)",
                    (course_id, content, score)
                )
                # 更新课程的最新评分
                conn.execute(
                    "UPDATE courses SET score = ? WHERE id = ?",
                    (score, course_id)
                )
            return True
        except sqlite3.Error:
            return False
    
    def update_score(self, course_id: int, score: float) -> bool:
        """更新课程评分"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE courses SET score = ? WHERE id = ?",
                    (score, course_id)
                )
            return True
        except sqlite3.Error:
            return False
    
    def get_feedback(self, course_id: int) -> List[tuple]:
        """获取课程反馈"""
        with sqlite3.connect(self.db_path) as conn:
            try:
                cursor = conn.execute("""
                    SELECT content, score, created_at 
                    FROM feedback 
                    WHERE course_id = ?
                    ORDER BY created_at DESC
                """, (course_id,))
                return cursor.fetchall()
            except sqlite3.OperationalError:
                # 如果score列不存在，返回带默认评分的结果
                cursor = conn.execute("""
                    SELECT content, created_at 
                    FROM feedback 
                    WHERE course_id = ?
                    ORDER BY created_at DESC
                """, (course_id,))
                return [(content, 0.0, created_at) for content, created_at in cursor.fetchall()]
    
    def clear_courses(self):
        """清空所有课程"""
        try:
            self.cursor.execute("DELETE FROM courses")
            self.conn.commit()
            return True
        except Exception as e:
            print(f"清空课程失败: {e}")
            return False
    
    def _clear_cache(self):
        """清除缓存"""
        self._cache.clear()
    
    def get_course_score(self, course_id: int) -> Optional[float]:
        """获取课程评分"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT score FROM courses WHERE id = ?",
                (course_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else None