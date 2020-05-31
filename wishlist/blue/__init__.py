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

# Config Logiing 
ERRORLOG_FILENAME = 'logs/error.log'
LOG_FILENAME = 'logs/log.log'

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

from blue.ui.users.views import users_blueprint
from blue.ui.books.views import books_blueprint
from blue.api.user.views import user_blueprint
from blue.api.book.views import book_blueprint
from blue.ui.views import site_blueprint

app.register_blueprint(users_blueprint, url_prefix=('/'))
app.register_blueprint(books_blueprint, url_prefix=('/'))
app.register_blueprint(site_blueprint, url_prefix=('/'))

app.register_blueprint(user_blueprint, url_prefix=('/user'))
app.register_blueprint(book_blueprint, url_prefix=('/book'))