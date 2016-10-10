

app.add_url_rule('/api/oauth/', 'oauth', views.oauth)
app.add_url_rule('/api/get_session/', 'get_session', views.get_session)
app.add_url_rule('/api/get_count_info/', 'get_count_info', views.get_count_info)
app.add_url_rule('/api/get_rank/', 'get_rank', views.get_rank)
app.add_url_rule('/api/do_sign/', 'do_sign', views.do_sign, methods=['POST'])
app.add_url_rule('/api/share/', 'share', views.share, methods=['POST'])
