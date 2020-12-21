import flask
from application import db
from werkzeug.security import generate_password_hash, check_password_hash
#from bson.objectid import ObjectId



class User(db.Document):
    _id         =   db.ObjectIdField()
    first_name  =   db.StringField( max_length=50 )
    last_name   =   db.StringField( max_length=50 )
    email       =   db.StringField( max_length=30, unique=True )
    password    =   db.StringField( )

    meta = {'db_alias': 'default'}

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def get_password(self, password):
        return check_password_hash(self.password, password)

class Project(db.Document):
    _id         =   db.ObjectIdField()
    project_name    =   db.StringField( max_length=100 )
    description     =   db.StringField( max_length=255 )
    user_id         =   db.ObjectIdField()

    meta = {'db_alias': 'default'}

class CalcInput(db.Document):
    _id             =   db.ObjectIdField()
    calc_name       =   db.StringField( max_length=100 )
    description     =   db.StringField( max_length=250 )
    calc_type_id    =   db.ObjectIdField()
    project_id      =   db.ObjectIdField( )
    calc_input_dict =   db.DictField()
    left_header     =   db.StringField( max_length=250 )
    center_header   =   db.StringField( max_length=250 )
    right_header    =   db.StringField( max_length=250 )

    meta = {'db_alias': 'default'}

class CalcType(db.Document):
    _id             =   db.ObjectIdField()
    type_name       =   db.StringField( max_length=100, unique=True)
    description     =   db.StringField( max_length=255 )
    file_name       =   db.StringField()

    meta = {'db_alias': 'default'}

class DeletedProject(db.Document):
    _id             =   db.ObjectIdField()
    previous_id     =   db.ObjectIdField()
    project_name    =   db.StringField( max_length=100 )
    description     =   db.StringField( max_length=255 )
    user_id         =   db.ObjectIdField()

    meta = {'db_alias': 'default'}

class DeletedCalc(db.Document):
    _id             =   db.ObjectIdField()
    calc_name       =   db.StringField( max_length=100 )
    description     =   db.StringField( max_length=250 )
    calc_type_id    =   db.ObjectIdField()
    project_id      =   db.ObjectIdField( )
    calc_input_dict =   db.DictField()

    meta = {'db_alias': 'default'}
