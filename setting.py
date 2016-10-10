#! -*- coding:utf8 -*-
# flask setting


class Flask_config:
    SECRET_KEY = 'sapoiudHJNA'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///D:/workspace/python/run_flask/test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True


BASE_URL = 'http://127.0.0.1:8080/'
AppID = '2f60b17e9d097f8f'
AppSecret = '3c8bbbdd9bf770459e7f32b490eccc9b'
YibanCallback = 'http://f.yiban.cn/iapp62419'

SHARE_DATA = {
    'share_title': '晨跑',
    'share_url': BASE_URL,
    'share_image': BASE_URL  # chose
}
