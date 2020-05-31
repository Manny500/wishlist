####### IMPORTS ########
from flask_wtf import FlaskForm
from wtforms import Form, StringField, TextAreaField, PasswordField, validators

# Register Form -------------------------------------------
class RegisterForm(Form):
    firstName = StringField('First Name', [validators.Length(min=1, max =50)])
    lastName = StringField('Last Name', [validators.Length(min=4, max =25)])
    email = StringField('Email', [validators.Length(min=2, max =50)])
    password =  PasswordField('Password', [
        validators.Length(min=4, max =50),
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
        ])
    confirm = PasswordField('Confirm Password')