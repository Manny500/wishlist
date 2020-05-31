####### IMPORTS ########
from flask_wtf import FlaskForm
from wtforms import Form, StringField, TextAreaField, PasswordField, validators

# Book Form
class BookForm(Form):
    isbn = StringField('ISBN', [validators.Length(min=1, max =50)])
    title = StringField('Title', [validators.Length(min=4, max =25)])
    author = StringField('Author', [validators.Length(min=6, max =50)])
    date = StringField('Date', [validators.Length(min=1, max =50)])