from wtforms import BooleanField, StringField, PasswordField, validators , ValidationError
from flask_wtf import FlaskForm, Form
from wtforms.validators import Email, DataRequired, InputRequired
from .models import User


class LoginForm(FlaskForm):
    email = StringField('Username',
                         id='username_login',
                         validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])
    remember = BooleanField('Remember',
                             id='rmb_login')

class ResetForm(FlaskForm):
    email = StringField('Email',
                      id='email_reset',
                      validators=[DataRequired(), Email()])

class RegistrationForm(FlaskForm):
    name = StringField('Username',
                        [validators.Length(min=4, max=25)])
    username = StringField('Username', 
                        [validators.Length(min=4, max=25)])
    email = StringField('Email',[validators.Length(min=6, max=35)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    remember = BooleanField('Remember' ,validators=[DataRequired()])
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

        
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
