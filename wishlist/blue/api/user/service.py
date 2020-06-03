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

from blue import app

# Import Logger
from blue import my_logger

# Import Models 
from blue.api.models import User
from blue.api.models import Owner

from blue.api.models import user_schema
from blue.api.models import users_schema

from blue.api.models import owner_schema
from blue.api.models import owners_schema

# Create class to call upon it
class Service:

    list = [] 

    #Constructor
    def __init__(self):
        self.list = list

####### User Logic ########
    # Delete a user
    def delete_user(self, id):

        try:
            user = User.query.get(id)
            db.session.delete(user)
            db.session.commit()
        except Exception as e:
            payload = {'error': e}
            my_logger.debug('Returning', payload['error'])
            return jsonify(payload)

        return user_schema.jsonify(user)

    # Update a user
    def update_user(self, id):


        try:
            user = User.query.get(id)
        except Exception as e:
            payload = {'error': e}
            my_logger.debug('Returning', payload['error'])
            return jsonify(payload)

        try:
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

        try:
            db.session.commit()
        except Exception as e:
            payload = {'error': e}
            my_logger.debug('Returning', payload['error'])
            return jsonify(payload)

        return user_schema.jsonify(user)
        
    # Get sigle user
    def get_user(self, id):

        try:
            user = User.query.get(id)
        except Exception as e:
            payload = {'error': e}
            my_logger.debug('Returning', payload['error'])
            return jsonify(payload)

        return user_schema.jsonify(user)

    # Get All Users
    def get_users(self):
            
        my_logger.debug('Entering get user GET')

        try:
            all_users = User.query.all()
        except Exception as e:
            payload = {'error': e}
            my_logger.debug('Returning', payload['error'])
            return jsonify(payload)
        
        payload = users_schema.dump(all_users)
        return jsonify(payload.data)

    # Create new User
    def new_user(self, request):

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

        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            payload = {'error': e}
            my_logger.debug('Returning', payload['error'])
            return jsonify(payload)
        
        payload = {'status': 'success'}
        return jsonify(payload)

    # User Login 
    def check_login(self, request):

        #Logs 
        my_logger.debug('Entering Check Login')

        try:
            # Get Login details
            email = request.json['email']
            password_candidate =request.json['password_candidate']
        except requests.exceptions.RequestException as e:
            error = e
            payload = {'error': error, 'email': ''}
            my_logger.debug('Returning', payload['error'])
            return jsonify(payload)

        # Query DB
        try:
            user = User.query.filter_by(email=email).first()
        except Exception as e:
            payload = {'error': e}
            my_logger.debug('Returning', payload['error'])
            return jsonify(payload)

        # If the user does exist
        if(user != None):

            try:
                password = user.password
            except Exception as e:
                payload = {'error': e}
                my_logger.debug('error', e)
                return jsonify(payload)

            # Compare passwords
            if sha256_crypt.verify(password_candidate, password):
                my_logger.debug('PASSWORD MATCHED')
                payload = {'email': user.email, 'firstName': user.firstName, 'id': user.id}
                my_logger.debug('Check Login Success')
                return jsonify(payload)
            else:
                my_logger.debug('PASSWORD NOT MATCHED')
                error = 'Invalid login'
                payload = {'error': error, 'email': ''}
                my_logger.debug('Check Login unsuccessful')
                return jsonify(payload)
        else:
            error = 'User email not found'
            payload = {'error': error, 'email': ''}
            my_logger.debug('Returning', payload['error'])
            return jsonify(payload)