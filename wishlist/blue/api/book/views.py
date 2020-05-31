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
    
    app.logger.info('PASSWORD MATCHED')

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
        my_logger.debug('Returning',payload)
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
    my_logger.debug('Returning',payload)

    return jsonify(payload)

# Get All Books for the user
@book_blueprint.route('/', methods=['GET'])
def get_books():

    my_logger.debug('Entering book GET')
    userID = request.args['id']
    all_books = db.session.execute('SELECT * FROM book WHERE id in (SELECT bookid FROM owner WHERE userid = :val)',{'val': userID})
    result = books_schema.dump(all_books)
    return jsonify(result)

# Get sigle book
@book_blueprint.route('/<id>', methods=['GET'])
def get_book(id):

    my_logger.debug('Entering book id POST')
    book = Book.query.get(id)
    return book_schema.jsonify(book)

# Update a book
@book_blueprint.route('/<id>', methods=['PUT'])
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
@book_blueprint.route('/<id>', methods=['DELETE'])
def delete_book(id):

    my_logger.debug('Entering book DELETE')
    book = Book.query.get(id)
    db.session.delete(book)
    db.session.commit()

    #Once a book is delete the ownership mapping should be delete as well
    Owner.query.filter(Owner.bookId == book.id).delete(synchronize_session=False)
    db.session.commit()

    return book_schema.jsonify(book)