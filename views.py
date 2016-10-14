#! -*- coding:utf8 -*-
import json
import sys
import time
import urllib2
from datetime import timedelta, date
from urllib import urlencode, quote

from flask import current_app
from flask import g
from flask import redirect
from flask import request
from flask import session

from app import db
from models import User, SignLog, Map
from setting import AppSecret, AppID, YibanCallback, BASE_URL, SHARE_DATA
from utils.login_require import login_required, admin_required
from utils.tools import decrypt, error, success, check_valid, get_type

reload(sys)  # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入
sys.setdefaultencoding('utf-8')


def oauth():
    auth_url = 'https://openapi.yiban.cn/oauth/authorize?client_id=%s&redirect_uri=%s&display=mobile' % (
        AppID, YibanCallback)
    if 'verify_request' in request.args:
        data = request.args['verify_request']
        user_info = decrypt(data, AppSecret, AppID)
        if user_info:
            if int(time.time()) - user_info.get('visit_time', 0) > 60 * 60 * 2:
                return '授权已过期，请重新授权'
            if not user_info['visit_oauth']:
                return redirect(auth_url)
            yiban_id = user_info['visit_user']['userid']
            token = user_info['visit_oauth']['access_token']
            user = User.query.get(yiban_id)
            if not user:
                yiban_info = json.loads(
                    urllib2.urlopen(url='https://openapi.yiban.cn/user/me?access_token=%s' % (token,)).read())
                if yiban_info['status'] != 'success':
                    return 'oAuth授权错误!!'
                yiban_info = yiban_info['info']
                user = User(yiban_id, yiban_info['yb_username'], yiban_info['yb_usernick'], yiban_info['yb_userhead'])
                user.save()
            session['yiban_id'] = yiban_id
            session['token'] = token
            if 'flag' in session:
                response = redirect(BASE_URL + 'result.html')
            elif 'admin' in session:
                response = redirect(BASE_URL + 'admin/index.html')
            else:
                response = redirect(BASE_URL + 'index.html')
            response.set_cookie('user_info', quote(json.dumps({'name': user.name, 'head': user.head_img})))
            return response
        else:
            return 'oAuth授权错误!!'
    else:
        if 'flag' in request.args:
            session['flag'] = int(request.args['flag'])
        else:
            if 'flag' in session:
                del session['flag']
        if 'admin' in request.args:
            session['admin'] = ' '
    return redirect(auth_url)


# 晨跑和早读统计
@login_required
def get_count_info():
    if 'both' in request.args:
        all = User.query.count()
        run_rank = User.query.filter(User.continue_run < g.user.continue_run).count()
        read_rank = User.query.filter(User.continue_read < g.user.continue_read).count()
        data = {'run': {
            'total': g.user.total_run,
            'continue': g.user.continue_run,
            'rank': int(run_rank / float(all) * 100)
        },
            'read': {
                'total': g.user.total_read,
                'continue': g.user.continue_read,
                'rank': int(read_rank / float(all) * 100)
            }}
    else:
        all = User.query.count()
        type = get_type(session.get('flag', 1))
        if type == 0:
            rank_count = User.query.filter(User.continue_read < g.user.continue_read).count()
        else:
            rank_count = User.query.filter(User.continue_run < g.user.continue_run).count()

        data = {
            'total': g.user.total_read,
            'continue': g.user.continue_read,
            'rank': int(rank_count / float(all) * 100)
        }
    return success(data)


# 连续签到排行
def get_rank():
    if 'both' not in request.args:
        type = get_type(session.get('flag', 0))
        if type == 0:
            data = _get_read_rank()
        else:
            data = _get_run_rank()
    else:
        data = {'run': _get_run_rank(), 'read': _get_read_rank()}
    return success(data)


def _get_run_rank():
    data = []
    tmp = User.query.order_by(User.continue_run.desc()).limit(10).all()
    for i in tmp:
        data.append({'id': i.id, 'name': i.name, 'head_img': i.head_img, 'count': i.continue_run})
    return data


def _get_read_rank():
    data = []
    tmp = User.query.order_by(User.continue_read.desc()).limit(10).all()
    for i in tmp:
        data.append({'id': i.id, 'name': i.name, 'head_img': i.head_img, 'count': i.continue_read})
    return data


@login_required
def do_sign():
    if 'flag' not in session:
        current_app.logger.error("'flag' not in session,yiban id %s" % g.user.id)
        return error('请在易班客户端扫码进入此页面')

    if not check_valid(int(session['flag']), float(request.form.get('latitude', 0)),
                       float(request.form.get('longitude', 0))):
        return error('位置信息有误')

    one_day = timedelta(days=1)
    today = date.today()
    yesterday = today - one_day
    type = get_type(session['flag'])

    if type == 0:
        if g.user.last_read < yesterday:
            g.user.continue_read = 1
        elif g.user.last_read == yesterday:
            g.user.continue_read += 1
        elif g.user.last_read == today:
            return error('今天已经签过到了')
        g.user.last_read = today
        g.user.total_read += 1
    else:
        if g.user.last_run < yesterday:
            g.user.continue_run = 1
        elif g.user.last_run == yesterday:
            g.user.continue_run += 1
        elif g.user.last_run == today:
            return error('今天已经签过到了')
        g.user.last_run = today
        g.user.total_run += 1
    sign = SignLog(int(session['flag']), request.form.get('location_des', ''),
                   request.form.get('latitude', ''),
                   request.form.get('longitude', ''), g.yiban_id)
    db.session.add(sign)
    db.session.add(g.user)
    db.session.commit()
    ranking = SignLog.query.filter(SignLog.type == type, SignLog.time == today).count()
    return success({'ranking': ranking})


def share():
    token = session.get('token')
    content = request.form.get('content')
    if not (token and content):
        return error('分享失败')
    data = SHARE_DATA
    data['access_token'] = token
    data['content'] = content

    res = json.loads(urllib2.urlopen(url='https://openapi.yiban.cn/share/send_share', data=urlencode(data)).read())
    if res.get('status') == 'success':
        return success()
    else:
        print res.get('info', []).get('msgCN')
        return error('分享失败')


@login_required
def get_session():
    # raise ValueError('测试错误')
    return str(session)


@admin_required
def get_flag():
    all = Map.query.all()
    data = []
    for i in all:
        data.append({'id': i.id, 'type': i.type, 'latitude': float(i.latitude), 'longitude': float(i.longitude)})
    return success(data)


@admin_required
def set_flag():
    if request.form.get('type'):
        type = int(request.form.get('type', 0))
        latitude = float(request.form.get('latitude', 0))
        longitude = float(request.form.get('longitude', 0))

    if not request.form.get('id'):
        m = Map(type, latitude, longitude)
        m.save()
        return success('成功创建')
    else:
        id = int(request.form.get('id'))
        m = Map.query.get(id)
        if request.form.get('delete'):
            m.delete()
            return success('成功删除')
        else:
            m.type = type
            m.latitude = latitude
            m.longitude = longitude
            m.save()
            return success('成功更新')
    return success('参数错误')


def user_info():
    id = request.args.get('id')
    if not id:
        return error()
    user = User.query.get(int(id))
    if not user:
        return error('用户不存在！')
    all = User.query.count()
    run_rank = User.query.filter(User.continue_run < user.continue_run).count()
    read_rank = User.query.filter(User.continue_read < user.continue_read).count()
    data = {
        'info': {
            'name': user.name,
            'head': user.head_img,
        },
        'run': {
            'total': user.total_run,
            'continue': user.continue_run,
            'rank': int(run_rank / float(all) * 100)
        },
        'read': {
            'total': user.total_read,
            'continue': user.continue_read,
            'rank': int(read_rank / float(all) * 100)
        },
        'history': []
    }
    tmp = user.sign_set.order_by(SignLog.id.desc()).limit(10).all()
    for i in tmp:
        time = '%d/%d' % (i.time.month, i.time.day)
        data['history'].append(
            {'type_id': i.type, 'location_des': i.location_des, 'latitude': i.latitude, 'longitude': i.longitude,
             'time': time})

    return success(data)
