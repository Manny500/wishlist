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
from blue.api.models import Book
from blue.api.models import Owner

from blue.api.models import book_schema
from blue.api.models import books_schema

from blue.api.models import owner_schema
from blue.api.models import owners_schema

# Create class to call upon it
class Service:

    list = [] 

    #Constructor
    def __init__(self):
        self.list = list

####### BOOK Logic ########
    # Delete a book
    def delete_book(self,id):

        my_logger.debug('Entering book DELETE')

        try:
            book = Book.query.get(id)
            db.session.delete(book)
            db.session.commit()
        except Exception as e:
            payload = {'error': e}
            my_logger.debug('error', e)
            return jsonify(payload)        

        #Once a book is delete the ownership mapping should be delete as well
        try:
            Owner.query.filter(Owner.bookId == book.id).delete(synchronize_session=False)
            db.session.commit()
        except Exception as e:
            payload = {'error': e}
            my_logger.debug('error', e)
            return jsonify(payload)

        return book_schema.jsonify(book)

# Update a book
    def update_book(self, request, id):

        my_logger.debug('Entering book PUT')

        try:
            book = Book.query.get(id)
        except Exception as e:
            payload = {'error': e}
            my_logger.debug('error', e)
            return jsonify(payload)

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

        try:
            db.session.commit()
        except Exception as e:
            payload = {'error': e}
            my_logger.debug('error', e)
            return jsonify(payload)

        return book_schema.jsonify(book)

# Get All Books for the user
    def get_books(self, request, id):

        my_logger.debug('Entering books GET')
        userID = request.args['id']

        try:
            all_books = db.session.execute('SELECT * FROM book WHERE id in (SELECT bookid FROM owner WHERE userid = :val)',{'val': userID})
        except Exception as e:
            payload = {'error': e}
            my_logger.debug('error', e)
            return jsonify(payload)

        payload = books_schema.dump(all_books)
        return jsonify(payload)

    # Get sigle book
    def get_book(self, id):

        #log the transaction
        my_logger.debug('Quering a single book')

        try:
            payload = Book.query.get(id)
        except Exception as e:
            payload = {'error': e}
            my_logger.debug('error', e)
            return jsonify(payload)

        if(payload == None):
            my_logger.debug('None found single book')
            payload = {'error': 'No book Found'}

        return book_schema.jsonify(payload)

# Create a Book
    def new_book(self, request):
        
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
            my_logger.debug('Returning', payload['error'])
            return jsonify(payload)

        #Check to see if there is already that book in the db
        #Assuming no book has the same  ISBN
        try:
            old_book = Book.query.filter_by(isbn=isbn).first()
        except Exception as e:
            payload = {'error': e}
            my_logger.debug('Returning', payload['error'])
            return jsonify(payload)
            
        #If there is no existing book, create one
        if(old_book == None):

            new_book = Book(isbn, title, author, date)

            try:
                db.session.add(new_book)
                db.session.commit()
            except Exception as e:
                payload = {'error': e}
                my_logger.debug('Returning', payload['error'])
                return jsonify(payload)

        #Get the id of the book in question
        try:
            db_book = Book.query.filter_by(isbn=isbn).first()
        except Exception as e:
            payload = {'error': e}
            my_logger.debug('Returning', payload['error'])
            return jsonify(payload)

        bookId = db_book.id

        #Mapp the new user ownership to the book
        new_owner = Owner(userId, bookId)

        try:
            db.session.add(new_owner)
            db.session.commit()
        except Exception as e:
            payload = {'error': e}
            my_logger.debug('Returning', payload['error'])
            return jsonify(payload)

        payload = {'status': 'success'}
        my_logger.debug('Returning', payload['status'])

        return jsonify(payload)