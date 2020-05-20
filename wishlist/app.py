from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session, logging
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
import os

from data import Books

# Init App
app = Flask(__name__)

# Set base URI
basedir = os.path.abspath(os.path.dirname(__file__))

# Config sqlite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'sqlite/db.wishlist')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init DB
db = SQLAlchemy(app)

#Init marshmallow
ma = Marshmallow(app) 

# Book Class/Model ------------------------------------------
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.Integer)
    title = db.Column(db.String(100))
    author = db.Column(db.String(100))
    date = db.Column(db.String(100))

    #Constructor
    def __init__(self, isbn, title, author, date):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.date = date

# Book schema
class BookSchema(ma.Schema):
    fields = ('id', 'isbn', 'title', 'author', 'date')

# Init Schema
book_schema = BookSchema()
books_schema = BookSchema(many=True)
Books = Books()

# User Class/Model ------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100))
    lastName = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

    #Constructor
    def __init__(self, firstName, lastName, email, password):
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.password = password

# Book schema
class UserSchema(ma.Schema):
    fields = ('id', 'firstName', 'lastName', 'email', 'password')

# Init Schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)

# Register Form -------------------------------------------
class RegisterForm(Form):
    firstName = StringField('First Name', [validators.Length(min=1, max =50)])
    lastName = StringField('Last Name', [validators.Length(min=4, max =25)])
    email = StringField('Email', [validators.Length(min=6, max =50)])
    password =  PasswordField('Password', [
        validators.Length(min=6, max =50),
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
        ])
    confirm = PasswordField('Confirm Password')

# Form Routes ---------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        firstName = form.firstName.data
        lastName = form.lastName.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #create cursor
        new_user = User(firstName, lastName, email, password)

        db.session.add(new_user)
        db.session.commit()

        flash('You have registered :)', 'success')

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# User Routes ---------------------------------------

# Register a User
@app.route('/user', methods=['POST'])
def add_user():
    firstName = request.json['firstName']
    lastName = request.json['lastName']
    email = request.json['email']
    password = request.json['password']

    new_user = User(firstName, lastName, email, password)

    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user)

# Get All Users
@app.route('/user', methods=['GET'])
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result.data)

# Get sigle user
@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    return user_schema.jsonify(user)

# Update a user
@app.route('/user/<id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)

    firstName = request.json['fistName']
    lastName = request.json['lastName']
    email = request.json['email']
    password = request.json['password']

    user.firstName = firstName
    user.lastName = lastName
    user.email = email
    user.password = password

    db.session.commit()
    return user_schema.jsonify(user)

# Delete a user
@app.route('/user/<id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return user_schema.jsonify(user)

# Book Routes ---------------------------------------

# Create a Book
@app.route('/book', methods=['POST'])
def add_book():
    isbn = request.json['name']
    title = request.json['title']
    author = request.json['author']
    date = request.json['date']

    new_book = Book(isbn, title, author, date)

    db.session.add(new_book)
    db.session.commit()

    return book_schema.jsonify(new_book)

# Get All Books
@app.route('/book', methods=['GET'])
def get_books():
    all_books = Book.query.all()
    result = books_schema.dump(all_books)
    return jsonify(result.data)

# Get sigle book
@app.route('/book/<id>', methods=['GET'])
def get_book(id):
    book = Book.query.get(id)
    return book_schema.jsonify(book)

# Update a book
@app.route('/book/<id>', methods=['PUT'])
def update_book(id):
    book = Book.query.get(id)

    isbn = request.json['isbn']
    title = request.json['title']
    author = request.json['author']
    date = request.json['date']

    book.isbn = isbn
    book.title = title
    book.author = author
    book.date = date

    db.session.commit()
    return book_schema.jsonify(book)

# Delete a book
@app.route('/book/<id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get(id)
    db.session.delete(book)
    db.session.commit()
    return book_schema.jsonify(book)

# Navigation Routes ---------------------------------------

# Set index
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/list')
def list():
    return render_template('list.html', books = Books)

@app.route('/list/<string:id>')
def details(id):
    return render_template('details.html', id=id)

# Create a simple get request
@app.route('/remove', methods=['GET'])
def get():
    return jsonify({'msg': 'Hello world'})

# Run server
if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)