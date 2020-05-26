####### IMPORTS ########
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from requests.exceptions import HTTPError
from marshmallow import Schema, fields
from passlib.hash import sha256_crypt
from logging import FileHandler, WARNING, DEBUG
from functools import wraps
import requests
import json
import glob
import logging.handlers

####### CONFIG ########
# Init App
app = Flask(__name__)

ERRORLOG_FILENAME = 'error_log.log'
LOG_FILENAME = 'log.log'


if not app.debug:
    # Init File handler
    file_handler = FileHandler(ERRORLOG_FILENAME)
    file_handler.setLevel(WARNING)

    app.logger.addHandler(file_handler)


# Set up a specific logger with our desired output level
my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.DEBUG)

# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=2000, backupCount=5)

my_logger.addHandler(handler)

# LOAD config file
app.config.from_pyfile('config.py')

# Init DB
db = SQLAlchemy(app)

#Init marshmallow
ma = Marshmallow(app) 

############################## MODELS ########################################
####### BOOK MODEL ########
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(100))
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
    id = fields.Integer()
    isbn = fields.Str()
    title = fields.Str()
    author = fields.Str()
    date = fields.Str()

# Init Schema
book_schema = BookSchema()
books_schema = BookSchema(many=True)

####### USER MODEL ########
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

# User schema
class UserSchema(ma.Schema):
    id = fields.Integer()
    firstName = fields.Str()
    lastName = fields.Str()
    email = fields.Str()
    password = fields.Str()

# Init Schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)

####### OWNER MODEL ########
class Owner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey("user.id"))
    bookId = db.Column(db.Integer, db.ForeignKey("book.id"))
    
    #Constructor
    def __init__(self, userId, bookId):
        self.userId = userId
        self.bookId = bookId

# Book schema
class OwnerSchema(ma.Schema):
    id = fields.Integer()
    userId = fields.Integer()
    bookId = fields.Integer()

# Init Schema
owner_schema = OwnerSchema()
owners_schema = OwnerSchema(many=True)

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
####### USER REST ENDPOINTS ########
# User Login 
@app.route('/check_login', methods=['POST'])
def check_login():

    #Logs 
    my_logger.debug('Entering Check Login')

    try:
        # Get Login details
        email = request.json['email']
        password_candidate =request.json['password_candidate']

    except requests.exceptions.RequestException as e:
        error = e
        payload = {'error': error, 'email': ''}
        my_logger.debug('Check Login Error')
        return jsonify(payload)

    # Query DB
    user = User.query.filter_by(email=email).first()

    # If the user does exist
    if(user != None):

        password = user.password

        # Compare passwords
        if sha256_crypt.verify(password_candidate, password):
            app.logger.info('PASSWORD MATCHED')
            payload = {'email': user.email, 'firstName': user.firstName, 'id': user.id}
            my_logger.debug('Check Login Success')
            return jsonify(payload)
        else:
            app.logger.info('PASSWORD NOT MATCHED')
            error = 'Invalid login'
            payload = {'error': error, 'email': ''}
            my_logger.debug('Check Login unsuccessful')
            return jsonify(payload)
    else:
        error = 'User email not found'
        payload = {'error': error, 'email': ''}
        my_logger.debug('Check Login Error')
        return jsonify(payload)


# Create new User
@app.route('/user', methods=['POST'])
def user():

    my_logger.debug('Entering get user POST')

    try:
        # Get User details
        firstName = request.json['firstName']
        lastName = request.json['lastName']
        email = request.json['email']
        password = request.json['password']

    except requests.exceptions.RequestException as e:
        error = e
        payload = {'error': error,}
        my_logger.debug('Check Login Error')
        return jsonify(payload)

    #DB instance
    new_user = User(firstName, lastName, email, password)
    db.session.add(new_user)
    db.session.commit()
    
    payload = {'status': 'success'}
    return jsonify(payload)

# Get All Users
@app.route('/user', methods=['GET'])
def get_users():
        
    my_logger.debug('Entering get user GET')
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result.data)

# Get sigle user
@app.route('/user/<id>', methods=['GET'])
def get_user(id):

    my_logger.debug('Entering get user id GET')

    user = User.query.get(id)
    return user_schema.jsonify(user)

# Update a user
@app.route('/user/<id>', methods=['PUT'])
def update_user(id):

    my_logger.debug('Entering get user id PUT')

    try:
        user = User.query.get(id)

        firstName = request.json['fistName']
        lastName = request.json['lastName']
        email = request.json['email']
        password = request.json['password']
    except requests.exceptions.RequestException as e:
        error = e
        payload = {'error': error}
        my_logger.debug('Check Login Error')
        return jsonify(payload)

    user.firstName = firstName
    user.lastName = lastName
    user.email = email
    user.password = password

    db.session.commit()
    return user_schema.jsonify(user)

# Delete a user
@app.route('/user/<id>', methods=['DELETE'])
def delete_user(id):

    my_logger.debug('Entering get user DELETE')
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return user_schema.jsonify(user)

####### BOOK REST ENDPOINTS ########
# Create a Book
@app.route('/book', methods=['POST'])
def new_book():

    try:
        my_logger.debug('Entering book POST')
        isbn = request.json['isbn']
        title = request.json['title']
        author = request.json['author']
        date = request.json['date']
        userId = request.json['userId']
    except requests.exceptions.RequestException as e:
        error = e
        payload = {'error': error}
        my_logger.debug('Check Login Error')
        return jsonify(payload)

    #Check to see if there is already that book in the db
    #Assuming no book has the same  ISBN
    old_book = Book.query.filter_by(isbn=isbn).first()

    #If there is no existing book, create one
    if(old_book == None):

        new_book = Book(isbn, title, author, date)

        db.session.add(new_book)
        db.session.commit()
    
    #Get the id of the book in question
    db_book = Book.query.filter_by(isbn=isbn).first()
    bookId = db_book.id

    #Mapp the new user ownership to the book
    new_owner = Owner(userId, bookId)

    db.session.add(new_owner)
    db.session.commit()

    payload = {'status': 'success'}
    return jsonify(payload)

# Get All Books for the user
@app.route('/book', methods=['GET'])
def get_books():

    my_logger.debug('Entering book GET')
    userID = request.args['id']
    all_books = db.session.execute('SELECT * FROM book WHERE id in (SELECT bookid FROM owner WHERE userid = :val)',{'val': userID})
    result = books_schema.dump(all_books)
    return jsonify(result)

# Get sigle book
@app.route('/book/<id>', methods=['GET'])
def get_book(id):

    my_logger.debug('Entering book id POST')
    book = Book.query.get(id)
    return book_schema.jsonify(book)

# Update a book
@app.route('/book/<id>', methods=['PUT'])
def update_book(id):

    my_logger.debug('Entering book PUT')
    book = Book.query.get(id)

    try:
        isbn = request.json['isbn']
        title = request.json['title']
        author = request.json['author']
        date = request.json['date']
    except requests.exceptions.RequestException as e:
        error = e
        payload = {'error': error}
        my_logger.debug('Check Login Error')
        return jsonify(payload)

    book.isbn = isbn
    book.title = title
    book.author = author
    book.date = date

    db.session.commit()
    return book_schema.jsonify(book)

# Delete a book
@app.route('/book/<id>', methods=['DELETE'])
def delete_book(id):

    my_logger.debug('Entering book DELETE')
    book = Book.query.get(id)
    db.session.delete(book)
    db.session.commit()

    #Once a book is delete the ownership mapping should be delete as well
    Owner.query.filter(Owner.bookId == book.id).delete(synchronize_session=False)
    db.session.commit()

    return book_schema.jsonify(book)

############################## UI ########################################
####### FORM ROUTES ########
@app.route('/register', methods=['GET', 'POST'])
def register():

    my_logger.debug('Entering register POST')

    #Get form validation and details
    form = RegisterForm(request.form)

    #IF form is submitted register the user
    if request.method == 'POST' and form.validate():

        #Get form info
        firstName = form.firstName.data
        lastName = form.lastName.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Build Request
        headers = {'Content-Type' : 'application/json'}
        payload = {'firstName': firstName, 'lastName': lastName, 'email': email, 'password': password}

        try:
            r = requests.post(API+'/user', data=json.dumps(payload),headers=headers)
        except requests.exceptions.RequestException as e:  
            raise SystemExit(e)

        json_string = r.json()

        if(json_string['status'] == 'success'):
            
            flash('You have registered :)', 'success')
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error=json_string['error'])
    return render_template('register.html', form=form)

####### LOGIN ROUTES ########
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

        try:
            r = requests.post(API+'/check_login', data=json.dumps(payload),headers=headers)
        except requests.exceptions.RequestException as e:  
            raise SystemExit(e)

        json_string = r.json()

        if(json_string['email'] != ''):

            # Passed same user info in session
            session['logged_in'] = True
            session['email'] = json_string['email']
            session['firstName'] = json_string['firstName']
            session['id'] = json_string['id']

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

####### BOOK ROUTES ########
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
        payload = {'isbn': isbn, 'title': title, 'author': author, 'date': date, 'userId': session['id']}
        
        try:
            r = requests.post(API+'/book', data=json.dumps(payload),headers=headers)
        except requests.exceptions.RequestException as e:  
            raise SystemExit(e)

        json_string = r.json()

        if(json_string['status'] == 'success'):
            
            flash('You have added a new book', 'success')
            return redirect(url_for('dashboard'))
        else:
            return render_template('add_book.html', error=json_string['error'])
    return render_template('add_book.html', form=form)

####### NAVIGATION ROUTES ########
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

    #Build the request
    headers = {'Content-Type' : 'application/json'}
    payload = {'id': session['id']}

    try:
        response = requests.get(API+'/book', params=payload, headers=headers) 
    except requests.exceptions.RequestException as e:  
        raise SystemExit(e)

    json_string = json.loads(response.text)

    if len(json_string) > 0:
        return render_template('list.html', books=json_string)
    else:
        msg = 'No Book found'
        return render_template('list.html', msg=msg)

# Set list of books
@app.route('/edit_book/<string:id>',methods=['GET','POST'])
@is_logged_in
def edit_book(id):

    #get the books info
    try:
        result = requests.get(API+'/book/'+id) 
    except requests.exceptions.RequestException as e:  
        raise SystemExit(e)

    json_result = result.json()

    form = BookForm(request.form)

    #Prepopulate the form
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

        try:
            response = requests.put(API+'/book/'+id, data=json.dumps(payload),headers=headers) 
        except requests.exceptions.RequestException as e:  
            raise SystemExit(e)

        json_string = response.json()

        if len(json_string) > 0:
            flash('Book Updated', 'success')
            return redirect(url_for('dashboard'))

    return render_template('edit_book.html', form=form)

# get a book detail
@app.route('/list/<string:id>', methods=['GET'])
@is_logged_in
def details(id):

    #Get book details
    try:
        response = requests.get(API+'/book/'+id) 
    except requests.exceptions.RequestException as e:  
        raise SystemExit(e)

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

    try:
        response = requests.delete(API+'/book/'+id) 
    except requests.exceptions.RequestException as e:  
        raise SystemExit(e)

    json_string = response.json()

    flash('Book deleted', 'success')
    return redirect(url_for('dashboard'))

# Go to Dashboard
@app.route('/dashboard', methods=['GET'])
@is_logged_in
def dashboard():

    headers = {'Content-Type' : 'application/json'}
    payload = {'id': session['id']}

    try:
        response = requests.get(API+'/book', params=payload, headers=headers) 
    except requests.exceptions.RequestException as e:  
        raise SystemExit(e)
    
    json_string = response.json()

    if len(json_string) > 0:
        return render_template('dashboard.html', books=json_string)
    else:
        msg = 'No Book found'
        return render_template('dashboard.html', msg=msg)

################ END OF ROUTES ######################

# Run server
if __name__ == '__main__':
    app.run()