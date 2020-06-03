####### IMPORTS ########
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session, logging, Blueprint
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from requests.exceptions import HTTPError
from logging import FileHandler, WARNING, DEBUG
import requests

# Import Logger
from blue import my_logger

# Import Service class 
from blue.api.book.service import Service

# Instantiate service class
service = Service()

####### Blueprint ########
book_blueprint = Blueprint(
    'book',
    __name__,
    template_folder='templates'
)

############################## API ########################################
####### BOOK REST ENDPOINTS ########
# Create a Book
@book_blueprint.route('', methods=['POST'])
def new_book():
    
    my_logger.debug('Entering New book POST')
    payload = service.new_book(request)
    return payload

# Get All Books for the user
@book_blueprint.route('/', methods=['GET'])
def get_books():

    my_logger.debug('Entering book GET')
    payload = service.get_books(request, id)
    return payload

# Get sigle book
@book_blueprint.route('/<id>', methods=['GET'])
def get_book(id):

    my_logger.debug('Entering book get single book id POST')
    book = service.get_book(id)
    return book

# Update a book
@book_blueprint.route('/<id>', methods=['PUT'])
def update_book(id):

    my_logger.debug('Entering update book PUT')
    payload = service.update_book(request, id)
    return payload

# Delete a book
@book_blueprint.route('/<id>', methods=['DELETE'])
def delete_book(id):

    my_logger.debug('Entering book DELETE')
    payload = service.delete_book(id)
    return payload