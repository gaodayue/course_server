#! /usr/bin/env python
# -*- coding: utf-8 -*-
from time import sleep
from datetime import datetime, time
from sns import WeiboClient
from pymongo import Connection
from pymongo.errors import ConnectionFailure

INTERVAL_MINUTE = 5

def is_closing(current_time, target_time, diff=15):
    def get_minutes(t):
        return 60 * t.hour + t.minute
    minutes_diff = get_minutes(target_time) - get_minutes(current_time)
    return (diff-INTERVAL_MINUTE) < minutes_diff <= diff

def next_course_session(t):
    session_time = [
            (1, time(8, 0)),
            (3, time(10,10)),
            (5, time(12,10)),
            (7, time(14,10)),
            (9, time(16,20)),
            (11,time(19,00)),
            (13,time(21,00))]
    for session,start_time in session_time:
        if is_closing(t, start_time):
            return session
    return 0

def week_of_term(today, startdate=datetime(2012, 2, 13).date()):
    delta_days = (today - startdate).days
    return delta_days / 7 + 1

def get_today_courses(today):
    week = week_of_term(today)
    day_of_week = today.isoweekday()
    try:
        connection = Connection()
    except ConnectionFailure, ex:
        print 'db connection failed'
        # TODO: should report error to admin
        return []
    db = connection['bjtu_courses']
    courses = db.courses.find(
            {"items.week":week, "items.d":day_of_week},
            {"name":1, "teacher":1, "students":1, "items":1})
    return courses

def send_weibo(class_info, students):
    text1 =  u"快上课了亲！%s的%s哦，在%s上哦，别忘记哦亲！" % \
            (class_info['teacher'], class_info['name'], class_info['where'])
    text2 = ' '.join(['@'+name for name in students])
    status = text1 + ' ' + text2
    weiboclient = WeiboClient()
    weiboclient.send_status(status)

def run():
    while True:
        now = datetime.now()
        session = next_course_session(now.time())
        sleeped_seconds = 0
        if session:
            today_courses = get_today_courses(now.date())
            for course in today_courses:
                for item in course['items']:
                    if session == item['session'][0]:
                        class_info = {}
                        class_info['name'] = course['name']
                        class_info['teacher'] = course['teacher']
                        class_info['session'] = session
                        class_info['where'] = item['where']
                        send_weibo(class_info, course['students'])
                        sleep(3)
                        sleeped_seconds += 3
        sleep(INTERVAL_MINUTE * 60 - sleeped_seconds)

if __name__ == '__main__':
    run()
