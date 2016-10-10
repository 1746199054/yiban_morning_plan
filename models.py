#! -*- coding:utf8 -*-
from datetime import datetime, timedelta, date

from decimal import Decimal

from app import db
from utils.tools import get_type


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    nick = db.Column(db.String(80))
    head_img = db.Column(db.String(255))
    total_run = db.Column(db.Integer, default=0)
    total_read = db.Column(db.Integer, default=0)
    continue_run = db.Column(db.Integer, default=0)
    continue_read = db.Column(db.Integer, default=0)
    last_run = db.Column(db.Date)
    last_read = db.Column(db.Date)

    def __init__(self, id, name, nick, head_img):
        self.id = id
        self.name = name
        self.nick = nick
        self.head_img = head_img
        one_day = timedelta(days=2)
        y_yesterday = date.today() - one_day
        self.last_run = y_yesterday
        self.last_read = y_yesterday

    def __repr__(self):
        return '<User %d,%s>' % (self.id, self.name)

    def save(self):
        db.session.add(self)
        db.session.commit()


class SignLog(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Integer)  # ('早读','晨跑')
    flag = db.Column(db.Integer)
    location_des = db.Column(db.String(255))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    time = db.Column(db.Date)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('sign_set', lazy='dynamic'))

    def __init__(self, flag, location_des, latitude, longitude, user_id):
        self.flag = flag
        self.type = get_type(flag)
        self.location_des = location_des
        self.latitude = latitude
        self.longitude = longitude
        self.user_id = user_id
        self.time = date.today()

    def __repr__(self):
        return '<User %d %s in %s at %s>' % (self.username, ('早读', '晨跑')[self.type], self.location_des, self.time)

    def save(self):
        db.session.add(self)
        db.session.commit()


class Map(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Integer)  # ('早读','晨跑')
    latitude = db.Column(db.DECIMAL(10, 6))
    longitude = db.Column(db.DECIMAL(10, 6))

    def __init__(self, type, latitude, longitude):
        self.type = type
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return '<Map latitude:%s latitude:%s %s>' % (self.latitude, self.longitude, ('早读', '晨跑')[self.type])

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
