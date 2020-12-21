
from flask import Flask
from config import Config
from flask_mongoengine import MongoEngine
# import redis
from flask_kvsession import KVSessionExtension
from simplekv.memory import DictStore

store = DictStore()


application = Flask(__name__)
application.config.from_object(Config)
KVSessionExtension(store, application) # overrides flask session to use simplekv storage (increase size)

db = MongoEngine()
db.init_app(application)

# calcdb = MongoEngine()
# calcdb.init_app(app)

from application import routes
