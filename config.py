import os
from private import P_SECRET_KEY, P_MONGODB_SETTINGS

class Config(object):
    SECRET_KEY = P_SECRET_KEY

    # MONGODB_SETTINGS = [{'ALIAS': 'default', 'DB' : 'ENCOMP_Main'}, {'ALIAS' : 'calc_db', 'DB':'ENCOMP_calcdata'}]
    MONGODB_SETTINGS = P_MONGODB_SETTINGS
