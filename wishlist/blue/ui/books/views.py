####### IMPORTS ########
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session, logging, Blueprint
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

# Import forms
from blue.ui.books.forms import BookForm

# Import Logger
from blue import my_logger

####### Blueprint ########
books_blueprint = Blueprint(
    'books',
    __name__,
    template_folder='templates'
)

# Constants
API = 'http://127.0.0.1:5000'

############################## LOGIC ########################################
# Check if user has logged in (Decorator)
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unathorized, Please Login', 'danger')
            return redirect(url_for('users.login'))
    return wrap
############################## UI ########################################
####### BOOK ROUTES ########
# Go to Add Book
@books_blueprint.route('/add_book', methods=['GET','POST'])
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
            response = requests.post(API+'/book', data=json.dumps(payload),headers=headers)
        except requests.exceptions.RequestException as e:  
            raise SystemExit(e)

        #my_logger.debug('Returning',response.text)

        json_string = response.json()

        if(json_string['status'] == 'success'):
            
            flash('You have added a new book', 'success')
            return redirect(url_for('site.dashboard'))
        else:
            return render_template('add_book.html', error=json_string['error'])
    return render_template('add_book.html', form=form)

# Set list of books
@books_blueprint.route('/list')
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
@books_blueprint.route('/edit_book/<string:id>',methods=['GET','POST'])
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
            return redirect(url_for('site.dashboard'))

    return render_template('edit_book.html', form=form)

# get a book detail
@books_blueprint.route('/list/<string:id>', methods=['GET'])
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
@books_blueprint.route('/del_book/<string:id>', methods=['POST'])
@is_logged_in
def del_book(id):

    try:
        response = requests.delete(API+'/book/'+id) 
    except requests.exceptions.RequestException as e:  
        raise SystemExit(e)

    json_string = response.json()

    flash('Book deleted', 'success')
    return redirect(url_for('site.dashboard'))