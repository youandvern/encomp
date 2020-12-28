import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'\xe8\x0f\x054-"\xa3\x8a\xa5\xea\x1b\xbc\xc9%<\xcf'

    # MONGODB_SETTINGS = [{'ALIAS': 'default', 'DB' : 'ENCOMP_Main'}, {'ALIAS' : 'calc_db', 'DB':'ENCOMP_calcdata'}]
    MONGODB_SETTINGS = [{'ALIAS': 'default', 'DB' : 'ENCOMP_Main', 'host':'52.201.7.126:27017' }, {'ALIAS' : 'calc_db', 'DB':'ENCOMP_calcdata', 'host':'52.201.7.126:27017' }]
