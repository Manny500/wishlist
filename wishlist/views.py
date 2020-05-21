from app import app
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session, logging
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import requests
from requests.exceptions import HTTPError
import json

# import db
from app import db
from app import ma

# Import Models
from models import User
from models import Book

from models import user_schema
from models import users_schema
from models import book_schema
from models import books_schema

# Import forms
from forms import RegisterForm
from forms import BookForm

# Constants
API = 'http://127.0.0.1:5000'
############################## METHODS ########################################

# Check if user has logged in (Decorator)
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unathorized, Please Login', 'danger')
            return redirect(url_for('login'))
    return wrap

############################## API ########################################
# User Login 
@app.route('/check_login', methods=['POST'])
def check_login():

    # Get Login details
    email = request.json['email']
    password_candidate =request.json['password_candidate']

    # Query DB
    user = User.query.filter_by(email=email).first()

    if(user != None):
        password = user.password

        # Compare passwords
        if sha256_crypt.verify(password_candidate, password):
            app.logger.info('PASSWORD MATCHED')
            payload = {'email': user.email, 'firstName': user.firstName}
            return jsonify(payload)
        else:
            app.logger.info('PASSWORD NOT MATCHED')
            error = 'Invalid login'
            payload = {'error': error, 'email': ''}
            return jsonify(payload)
    else:
        error = 'User email not found'
        payload = {'error': error, 'email': ''}
        return jsonify(payload)

#Create new User
@app.route('/user', methods=['POST'])
def user():

    # Get User details
    firstName = request.json['firstName']
    lastName = request.json['lastName']
    email = request.json['email']
    password = request.json['password']

    #DB instance
    new_user = User(firstName, lastName, email, password)
    db.session.add(new_user)
    db.session.commit()
    
    payload = {'status': 'success'}
    return jsonify(payload)

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

#Book Routes ---------------------------------------
# Create a Book
@app.route('/book', methods=['POST'])
def new_book():

    isbn = request.json['isbn']
    title = request.json['title']
    author = request.json['author']
    date = request.json['date']

    new_book = Book(isbn, title, author, date)

    db.session.add(new_book)
    db.session.commit()

    payload = {'status': 'success'}
    return jsonify(payload)

# Get All Books
@app.route('/book', methods=['GET'])
def get_books():
    all_books = Book.query.all()
    result = books_schema.dump(all_books)
    return jsonify(result)

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


############################## UI ########################################
# Form Routes ---------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        firstName = form.firstName.data
        lastName = form.lastName.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Build Request
        headers = {'Content-Type' : 'application/json'}
        payload = {'firstName': firstName, 'lastName': lastName, 'email': email, 'password': password}
        r = requests.post(API+'/user', data=json.dumps(payload),headers=headers)

        json_string = r.json()

        if(json_string['status'] == 'success'):
            
            flash('You have registered :)', 'success')
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error=json_string['error'])
    return render_template('register.html', form=form)
# User Routes ---------------------------------------
# User Login 
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        #Get Form fields
        email = request.form['email']
        password_candidate = request.form['password']

        # Build Request
        headers = {'Content-Type' : 'application/json'}
        payload = {'email': email, 'password_candidate': password_candidate}
        r = requests.post(API+'/check_login', data=json.dumps(payload),headers=headers)

        json_string = r.json()

        if(json_string['email'] != ''):
            # Passed
            session['logged_in'] = True
            session['email'] = json_string['email']
            session['firstName'] = json_string['firstName']

            flash('You have successfully logged in', 'success')
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error=json_string['error'])
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have successfully logged out', 'success')
    return redirect(url_for('login'))

# Go to Add Book
@app.route('/add_book', methods=['GET','POST'])
@is_logged_in
def add_book():
    form = BookForm(request.form)
    if request.method == 'POST' and form.validate():
        isbn = form.isbn.data
        title = form.title.data
        author = form.author.data
        date = form.date.data
        
        # Build Request
        headers = {'Content-Type' : 'application/json'}
        payload = {'isbn': isbn, 'title': title, 'author': author, 'date': date}
        r = requests.post(API+'/book', data=json.dumps(payload),headers=headers)

        json_string = r.json()

        if(json_string['status'] == 'success'):
            
            flash('You have added a new book', 'success')
            return redirect(url_for('dashboard'))
        else:
            return render_template('add_book.html', error=json_string['error'])
    return render_template('add_book.html', form=form)

# Navigation Routes ---------------------------------------
# Set index
@app.route('/')
def index():
    return render_template('home.html')

# Set about page
@app.route('/about')
def about():
    return render_template('about.html')

# Set list of books
@app.route('/list')
@is_logged_in
def list():
    response = requests.get(API+'/book') 

    json_string = response.json()

    if len(json_string) > 0:
        return render_template('list.html', books=json_string)
    else:
        msg = 'No Book found'
        return render_template('list.html', msg=msg)

# Set list of books
@app.route('/edit_book/<string:id>',methods=['GET','POST'])
@is_logged_in
def edit_book(id):

    result = requests.get(API+'/book/'+id) 

    json_result = result.json()

    form = BookForm(request.form)

    form.isbn.data = json_result['isbn']
    form.title.data = json_result['title']
    form.author.data = json_result['author']
    form.date.data = json_result['date']
    
    if request.method == 'POST' and form.validate():

        isbn = request.form['isbn']
        title = request.form['title']
        author = request.form['author']
        date = request.form['date']

        # Build Request
        headers = {'Content-Type' : 'application/json'}
        payload = {'isbn': isbn, 'title': title, 'author': author, 'date': date}
        response = requests.put(API+'/book/'+id, data=json.dumps(payload),headers=headers) 

        json_string = response.json()

        if len(json_string) > 0:
            flash('Book Updated', 'success')
            return redirect(url_for('dashboard'))
    return render_template('edit_book.html', form=form)

# get a book detail
@app.route('/list/<string:id>', methods=['GET'])
@is_logged_in
def details(id):
    response = requests.get(API+'/book/'+id) 

    json_string = response.json()

    if len(json_string) > 0:
        return render_template('details.html', book=json_string)
    else:
        msg = 'No Book found'
        return render_template('details.html', msg=msg)

# Delete a book detail
@app.route('/del_book/<string:id>', methods=['POST'])
@is_logged_in
def del_book(id):
    response = requests.delete(API+'/book/'+id) 

    json_string = response.json()

    flash('Book deleted', 'success')
    return redirect(url_for('dashboard'))

# Go to Dashboard
@app.route('/dashboard', methods=['GET'])
@is_logged_in
def dashboard():
    response = requests.get(API+'/book') 

    json_string = response.json()

    if len(json_string) > 0:
        return render_template('dashboard.html', books=json_string)
    else:
        msg = 'No Book found'
        return render_template('dashboard.html', msg=msg)