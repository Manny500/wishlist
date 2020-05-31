####### IMPORTS ########
from marshmallow import Schema, fields

from blue import db
from blue import ma

############################## MODELS ########################################
####### BOOK MODEL ########
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(100))
    title = db.Column(db.String(100))
    author = db.Column(db.String(100))
    date = db.Column(db.String(100))

    #Constructor
    def __init__(self, isbn, title, author, date):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.date = date

# Book schema
class BookSchema(ma.Schema):
    id = fields.Integer()
    isbn = fields.Str()
    title = fields.Str()
    author = fields.Str()
    date = fields.Str()

# Init Schema
book_schema = BookSchema()
books_schema = BookSchema(many=True)

####### USER MODEL ########
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100))
    lastName = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

    #Constructor
    def __init__(self, firstName, lastName, email, password):
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.password = password

# User schema
class UserSchema(ma.Schema):
    id = fields.Integer()
    firstName = fields.Str()
    lastName = fields.Str()
    email = fields.Str()
    password = fields.Str()

# Init Schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)

####### OWNER MODEL ########
class Owner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey("user.id"))
    bookId = db.Column(db.Integer, db.ForeignKey("book.id"))
    
    #Constructor
    def __init__(self, userId, bookId):
        self.userId = userId
        self.bookId = bookId

# Book schema
class OwnerSchema(ma.Schema):
    id = fields.Integer()
    userId = fields.Integer()
    bookId = fields.Integer()

# Init Schema
owner_schema = OwnerSchema()
owners_schema = OwnerSchema(many=True)