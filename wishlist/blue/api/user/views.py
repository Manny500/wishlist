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
from blue.api.user.service import Service

# Instantiate service class
service = Service()

####### Blueprint ########
user_blueprint = Blueprint(
    'user',
    __name__,
    template_folder='templates'
)

############################## API ########################################
####### USER REST ENDPOINTS ########
# User Login 
@user_blueprint.route('/check_login', methods=['POST'])
def check_login():

    my_logger.debug('Entering Check Login')
    payload = service.check_login(request)
    return payload


# Create new User
@user_blueprint.route('', methods=['POST'])
def new_user():

    my_logger.debug('Entering get user POST')
    payload = service.new_user(request)
    return payload

# Get All Users
@user_blueprint.route('/', methods=['GET'])
def get_users():
        
    my_logger.debug('Entering get users GET')
    payload = service.get_users()
    return payload

# Get sigle user
@user_blueprint.route('/<id>', methods=['GET'])
def get_user(id):

    my_logger.debug('Entering get user id GET')
    payload = service.get_user(id)
    return payload

# Update a user
@user_blueprint.route('/<id>', methods=['PUT'])
def update_user(id):

    my_logger.debug('Entering get user id PUT')
    payload = service.update_user(id)
    return payload

# Delete a user
@user_blueprint.route('/<id>', methods=['DELETE'])
def delete_user(id):

    my_logger.debug('Entering get user DELETE')
    payload = service.delete_user(id)
    return payload