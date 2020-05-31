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
from blue.ui.users.forms import RegisterForm

# Import Logger
from blue import my_logger

####### Blueprint ########
site_blueprint = Blueprint(
    'site',
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
####### NAVIGATION ROUTES ########
# Set index
@site_blueprint.route('/')
def index():
    return render_template('home.html')

# Set about page
@site_blueprint.route('/about')
def about():
    return render_template('about.html')

# Go to Dashboard
@site_blueprint.route('/dashboard', methods=['GET'])
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

####### USER FORM ROUTES ########
@site_blueprint.route('/register', methods=['GET', 'POST'])
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
            return redirect(url_for('users.login'))
        else:
            return render_template('register.html', error=json_string['error'])
    return render_template('register.html', form=form)
