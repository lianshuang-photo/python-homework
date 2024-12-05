from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from datetime import datetime
from typing import List
from models import Course

def export_to_pdf(courses: List[Course], filename: str):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []

    # 创建表格数据
    data = [['时间', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']]
    
    # 初始化时间表
    time_slots = {}
    for hour in range(8, 20):  # 8:00 - 19:00
        for course in courses:
            if course.start_time.hour <= hour < course.end_time.hour:
                if hour not in time_slots:
                    time_slots[hour] = [f"{hour}:00"] + [""] * 7
                time_slots[hour][course.weekday + 1] = f"{course.name}\n{course.teacher}\n{course.location}"

    # 填充数据
    for hour in range(8, 20):
        if hour in time_slots:
            data.append(time_slots[hour])
        else:
            data.append([f"{hour}:00"] + [""] * 7)

    # 创建表格
    table = Table(data)
    
    # 设置表格样式
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('WORDWRAP', (0, 0), (-1, -1), True),
    ])
    table.setStyle(style)
    
    elements.append(table)
    doc.build(elements)

def export_to_ical(courses: List[Course], filename: str):
    from icalendar import Calendar, Event
    from datetime import date, timedelta
    
    cal = Calendar()
    cal.add('prodid', '-//课表管理系统//mxm.dk//')
    cal.add('version', '2.0')
    
    # 获取本周一的日期
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    
    # 为每个课程创建事件
    for course in courses:
        event = Event()
        event.add('summary', course.name)
        
        # 计算课程日期
        course_date = monday + timedelta(days=course.weekday)
        
        # 设置开始和结束时间
        start_dt = datetime.combine(course_date, course.start_time)
        end_dt = datetime.combine(course_date, course.end_time)
        
        event.add('dtstart', start_dt)
        event.add('dtend', end_dt)
        event.add('location', course.location)
        event.add('description', f"教师: {course.teacher}\n{course.description or ''}")
        
        # 设置每周重复
        event.add('rrule', {'freq': 'weekly'})
        
        cal.add_component(event)
    
    # 保存到文件
    with open(filename, 'wb') as f:
        f.write(cal.to_ical())
