#! -*- coding:utf8 -*-
from flask import Flask

from setting import Flask_config
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Flask_config)
db = SQLAlchemy(app)


