
from flask import Flask
from config import Config
from flask_mongoengine import MongoEngine
from flask_mail import Mail
# import redis
from flask_kvsession import KVSessionExtension
from simplekv.memory import DictStore
import os

store = DictStore()


application = Flask(__name__)
application.config.from_object(Config)
KVSessionExtension(store, application) # overrides flask session to use simplekv storage (increase size)

application.config["MAIL_SERVER"] = 'smtp.zoho.com'
application.config["MAIL_PORT"] = 465
application.config["MAIL_USE_SSL"] = True
application.config["MAIL_USERNAME"] = 'team@encompapp.com'
application.config["MAIL_PASSWORD"] = os.environ['ZOHO_EMAIL_PASSWORD']

mail = Mail(application)

db = MongoEngine()
db.init_app(application)

# calcdb = MongoEngine()
# calcdb.init_app(app)

from application import routes
