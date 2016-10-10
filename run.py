#! -*- coding:utf8 -*-
import views
from app import app

app.add_url_rule('/api/oauth/', 'oauth', views.oauth)
app.add_url_rule('/api/get_session/', 'get_session', views.get_session)
app.add_url_rule('/api/get_count_info/', 'get_count_info', views.get_count_info)
app.add_url_rule('/api/get_rank/', 'get_rank', views.get_rank)
app.add_url_rule('/api/do_sign/', 'do_sign', views.do_sign, methods=['POST'])
app.add_url_rule('/api/share/', 'share', views.share, methods=['POST'])
app.add_url_rule('/api/get_flag/', 'get_flag', views.get_flag)
app.add_url_rule('/api/set_flag/', 'set_flag', views.set_flag, methods=['POST'])
app.add_url_rule('/api/admin_login/', 'admin_login', views.admin_login, methods=['POST'])

app.debug = True
if not app.debug:
    import logging
    from logging.handlers import SMTPHandler

    mail_handler = SMTPHandler('smtp.cqu.edu.cn',
                               '20154232@cqu.edu.cn',
                               ['wang0.618@qq.com'], '应用出错', ('20154232@cqu.edu.cn', 'ABC31415926535'))
    file_handler = logging.FileHandler('./log/log.txt')
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter('''
    Message type:       %(levelname)s
    Location:           %(pathname)s:%(lineno)d
    Module:             %(module)s
    Function:           %(funcName)s
    Time:               %(asctime)s

    Message:

    %(message)s
    '''))
    app.logger.addHandler(mail_handler)
    app.logger.addHandler(file_handler)

if __name__ == '__main__':
    app.run()
