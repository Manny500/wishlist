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

# Import DB
from blue import db
from blue import ma

# Import Models 
from blue.api.models import User

from blue.api.models import user_schema
from blue.api.models import users_schema

# Import Logger
from blue import my_logger

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
            #app.logger.info('PASSWORD MATCHED')
            payload = {'email': user.email, 'firstName': user.firstName, 'id': user.id}
            my_logger.debug('Check Login Success')
            return jsonify(payload)
        else:
            #app.logger.info('PASSWORD NOT MATCHED')
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
@user_blueprint.route('', methods=['POST'])
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
@user_blueprint.route('/', methods=['GET'])
def get_users():
        
    my_logger.debug('Entering get user GET')
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result.data)

# Get sigle user
@user_blueprint.route('/<id>', methods=['GET'])
def get_user(id):

    my_logger.debug('Entering get user id GET')

    user = User.query.get(id)
    return user_schema.jsonify(user)

# Update a user
@user_blueprint.route('/<id>', methods=['PUT'])
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
@user_blueprint.route('/<id>', methods=['DELETE'])
def delete_user(id):

    my_logger.debug('Entering get user DELETE')
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return user_schema.jsonify(user)