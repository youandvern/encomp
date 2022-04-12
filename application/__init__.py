
from flask import Flask
from config import Config
from private import p_mail_config
from flask_mongoengine import MongoEngine
from flask_mail import Mail
from flask_kvsession import KVSessionExtension
from simplekv.memory import DictStore
import os

store = DictStore()


application = Flask(__name__)
application.config.from_object(Config)
KVSessionExtension(store, application) # overrides flask session to use simplekv storage (increase size)

application.config["MAIL_SERVER"] = p_mail_config.get("MAIL_SERVER")
application.config["MAIL_PORT"] = p_mail_config.get("MAIL_PORT")
application.config["MAIL_USE_SSL"] = p_mail_config.get("MAIL_USE_SSL")
application.config["MAIL_USERNAME"] = p_mail_config.get("MAIL_USERNAME")
application.config["MAIL_PASSWORD"] = p_mail_config.get("MAIL_PASSWORD")

mail = Mail(application)

db = MongoEngine()
db.init_app(application)

# calcdb = MongoEngine()
# calcdb.init_app(app)

from application import routes
