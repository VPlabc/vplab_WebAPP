from wtforms import Form, StringField, TextAreaField, PasswordField,SubmitField,validators, ValidationError,BooleanField
from flask_wtf.file import FileRequired,FileAllowed, FileField
from wtforms.fields import DateField
from wtforms.validators import Email, DataRequired, InputRequired
from flask_wtf import FlaskForm
from .model import Register




class CustomerRegisterForm(FlaskForm):
    name = StringField('Name: ')
    username = StringField('Username: ', [validators.DataRequired()])
    email = StringField('Email: ', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password: ', [validators.DataRequired(), validators.EqualTo('confirm', message=' Mật khẩu không khớp nhau! ')])
    confirm = PasswordField('Repeat Password: ', [validators.DataRequired()])
    country = StringField('Country: ', [validators.DataRequired()])
    city = StringField('City: ', [validators.DataRequired()])
    contact = StringField('Contact: ', [validators.DataRequired()])
    address = StringField('Address: ', [validators.DataRequired()])
    zipcode = StringField('Zip code: ', [validators.DataRequired()])
    birthday = DateField('Birthday', format='%d-%m-%Y')
    gender = StringField('Gender: ', [validators.DataRequired()])
    role = StringField('Role: ')
    dated = StringField('Dated: ')
    remember = BooleanField('Remember' ,validators=[DataRequired()])
    profile = FileField('Profile', validators=[FileAllowed(['jpg','png','jpeg','gif'], 'Image only please')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        if Register.query.filter_by(username=username.data).first():
            raise ValidationError("Tài khoản này đã đăng kí rồi!!!")
        
    def validate_email(self, email):
        if Register.query.filter_by(email=email.data).first():
            raise ValidationError("Địa chỉ email này đã đăng kí rồi!!!")

    


class CustomerLoginFrom(FlaskForm):
    email = StringField('Username',
                         id='username_login',
                         validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])
    remember = BooleanField('Remember',
                             id='rmb_login')

   




   

 

    

     

   


    

