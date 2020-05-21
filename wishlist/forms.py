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

# Book Form
class BookForm(Form):
    isbn = StringField('ISBN', [validators.Length(min=1, max =50)])
    title = StringField('Title', [validators.Length(min=4, max =25)])
    author = StringField('Author', [validators.Length(min=6, max =50)])
    date = StringField('Date', [validators.Length(min=1, max =50)])