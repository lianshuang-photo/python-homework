import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from typing import List
from models import Course

SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarSync:
    def __init__(self):
        self.creds = None
        self.service = None
        
    def authenticate(self):
        """处理 Google Calendar API 认证"""
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
                
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    raise FileNotFoundError(
                        "请先从 Google Cloud Console 下载 credentials.json 文件"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
                
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('calendar', 'v3', credentials=self.creds)
        
    def sync_courses(self, courses: List[Course]):
        """将课程同步到 Google Calendar"""
        if not self.service:
            self.authenticate()
            
        # 获取当前周的开始日期（周一）
        today = datetime.now().date()
        monday = today - timedelta(days=today.weekday())
        
        # 创建日历事件
        for course in courses:
            # 计算课程日期
            course_date = monday + timedelta(days=course.weekday)
            
            # 设置事件开始和结束时间
            start_time = datetime.combine(course_date, course.start_time)
            end_time = datetime.combine(course_date, course.end_time)
            
            event = {
                'summary': course.name,
                'location': course.location,
                'description': f"教师: {course.teacher}\n{course.description or ''}",
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Asia/Shanghai',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Asia/Shanghai',
                },
                'recurrence': [
                    'RRULE:FREQ=WEEKLY'
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 15},
                    ],
                },
            }
            
            # 检查是否已存在相同的事件
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_time.isoformat() + 'Z',
                timeMax=(start_time + timedelta(minutes=1)).isoformat() + 'Z',
                q=course.name
            ).execute()
            
            existing_events = events_result.get('items', [])
            
            if existing_events:
                # 更新现有事件
                event_id = existing_events[0]['id']
                self.service.events().update(
                    calendarId='primary',
                    eventId=event_id,
                    body=event
                ).execute()
            else:
                # 创建新事件
                self.service.events().insert(
                    calendarId='primary',
                    body=event
                ).execute()
