#! -*- coding:utf8 -*-
import os, sys
from datetime import timedelta, datetime
from datetime import date
from os.path import dirname

sys.path.append(dirname(dirname(os.path.realpath(__file__))))

from app import db
from models import User


def update_continue_data():
    """更新数据库中连续签到的信息
    cron每天00:01触发
    """
    try:
        one_day = timedelta(days=1)
        today = date.today()
        yesterday = today - one_day
        read_update_count = User.query.filter(User.last_read < yesterday, User.continue_read != 0).update(
            {'continue_read': 0})
        run_update_count = User.query.filter(User.last_run < yesterday, User.continue_run != 0).update(
            {'continue_run': 0})
        db.session.commit()
        return '%s update success,run:%d read:%d' % (today, read_update_count, run_update_count)
    except Exception as e:
        return '%s update fail,error msg:%s' % (today, e)


p = os.path.join(dirname(dirname(os.path.realpath(__file__))), 'log', 'cron.log')
with open(p, 'a') as f:
    data = '%s, %s\n' % (datetime.now(), update_continue_data())
    f.write(data)
    print data
