#! -*- coding:utf8 -*-
from functools import wraps

from flask import current_app
from flask import g
from flask import session

from models import User
from utils.tools import error


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'yiban_id' not in session:
            return error('未进行易班授权，请重新进入应用！', 10)
        g.yiban_id = session['yiban_id']
        g.token = session['token']
        g.user = User.query.get(session['yiban_id'])
        if current_app.debug:
            return f(*args, **kwargs)
        else:
            try:
                return f(*args, **kwargs)
            except Exception, e:
                current_app.logger.error('视图出错，%s' % str(e))
                return error('未知错误')

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'yiban_id' not in session:
            return error('未登陆', 10)
        if session.get('yiban_id', '') not in ['5566213']:
            return error('没有权限', 1)
        if current_app.debug:
            return f(*args, **kwargs)
        else:
            try:
                return f(*args, **kwargs)
            except Exception, e:
                current_app.logger.error('视图出错，%s' % str(e))
                return error('未知错误')

    return decorated_function
