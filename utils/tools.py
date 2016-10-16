#! -*- coding:utf8 -*-
import json

from Crypto.Cipher import AES


def success(result=None):
    return json.dumps({'status': True, 'data': result})


def error(msg, code=0):
    return json.dumps({'status': False, 'msg': msg, 'code': code})


def h2b(s):
    import array, string
    ar = array.array('c')
    start = 0
    if s[:2] == '0x':
        start = 2
    for i in range(start, len(s), 2):
        num = string.atoi("%s" % (s[i:i + 2],), 16)
        ar.append(chr(num))
    return ar.tostring()


def decrypt(data, app_secret, app_id):
    try:
        mode = AES.MODE_CBC
        data = h2b(data)
        decryptor = AES.new(app_secret, mode, IV=app_id)
        plain = decryptor.decrypt(data)
        # plain = "".join([plain.strip().rsplit("}", 1)[0], "}"])
        oauth_state = json.loads(plain.rstrip(chr(0)))
        return oauth_state
    except Exception as e:
        return False


from math import radians, cos, sin, asin, sqrt


def distance(lon1, lat1, lon2, lat2):  # 经度1，纬度1，经度2，纬度2 （十进制度数）
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # 将十进制度数转化为弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # 地球平均半径，单位为公里
    return c * r * 1000


def check_valid(flag, latitude, longitude):
    try:
        from models import Map
        m = Map.query.get(flag)
        d = distance(longitude, latitude, float(m.longitude), float(m.latitude))
        if d > 100:
            return (False, '')
        else:
            return (True, m.name)
    except Exception as e:
        from flask import current_app
        current_app.logger.error('检查经纬度有效性出错，%s' % str(e))
        return (False, '')


def get_type(type):
    try:
        from models import Map
        m = Map.query.get(type)
        return m.type
    except Exception as e:
        return 0


if __name__ == '__main__':
    print distance(106.299564, 29.596987, 106.30032, 29.595375)
