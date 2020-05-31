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
users_blueprint = Blueprint(
    'users',
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
####### LOGIN ROUTES ########
# User Login 
@users_blueprint.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        #Get Form fields
        email = request.form['email']
        password_candidate = request.form['password']

        # Build Request
        headers = {'Content-Type' : 'application/json'}
        payload = {'email': email, 'password_candidate': password_candidate}

        try:
            r = requests.post(API+'/user/check_login', data=json.dumps(payload),headers=headers)
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
            return redirect(url_for('site.dashboard'))
        else:
            return render_template('login.html', error=json_string['error'])
    return render_template('login.html')

# Logout
@users_blueprint.route('/logout')
def logout():
    session.clear()
    flash('You have successfully logged out', 'success')
    return redirect(url_for('users.login'))
