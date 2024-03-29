from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from application.models import User, CalcType


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=20)])
    remember_me = BooleanField("Remember Me")
    login_submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    emailR = StringField("Email", validators=[DataRequired(), Email()])
    passwordR = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=20, message='Password must be 6-20 characters.')])
    password_confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('passwordR', message='Passwords do not match.')])
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    register_submit = SubmitField("Create Account")

    def validate_email(self, email):
        if user := User.objects(email=emailR.data).first():
            raise ValidationError("Email is already registered.")

class ProjectForm(FlaskForm):
    project_name = StringField("Project Name", validators=[DataRequired()])
    description = StringField("Project Description")
    submit = SubmitField("Add New Project")

class ChangeProjectForm(FlaskForm):
    new_project_name = StringField("Project Name", validators=[DataRequired()])
    new_description = StringField("Project Description")
    submit = SubmitField("Update Project Name")

class CalcForm(FlaskForm):
    def get_type_names():
        types = CalcType.objects().all()
        return [type.type_name for type in types]
    calc_name = StringField("Calculation Name", validators=[DataRequired()])
    description = StringField("Calculation Description")
    calc_type = SelectField("Choose Calculation Type", choices=get_type_names(), validators=[DataRequired()])
    submit = SubmitField("Add New Calculation")

class ChangeCalcForm(FlaskForm):
    new_calc_name = StringField("Calculation Name", validators=[DataRequired()])
    new_description = TextAreaField("Calculation Description")
    new_left_header = TextAreaField("Left Header")
    new_center_header = TextAreaField("Center Header")
    new_right_header = TextAreaField("Right Header")
    change_calc_name = SubmitField("Update Calculation Name") # submit button


class CalcTypeForm(FlaskForm):
    type_name = StringField("Calculation Name", validators=[DataRequired()])
    description = StringField("Calculation Description")
    submit = SubmitField("Add New Project")


class ContactForm(FlaskForm):
    name = StringField("Name",  validators=[DataRequired()])
    email = StringField("Email",  validators=[DataRequired(), Email()])
    subject = StringField("Subject",  validators=[DataRequired()])
    message = TextAreaField("Message",  validators=[DataRequired()])
    submit = SubmitField("Send")
