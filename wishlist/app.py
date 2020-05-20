from flask import Flask, render_template, request, jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
import os

from data import Books

# Init App
app = Flask(__name__)

# Set base URI
basedir = os.path.abspath(os.path.dirname(__file__))

# Config sqlite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'sqlite/db.wishlist')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init DB
db = SQLAlchemy(app)

#Init marshmallow
ma = Marshmallow(app) 

# Book Class/Model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.Integer)
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
    fields = ('id', 'isbn', 'title', 'author', 'date')

# Init Schema
book_schema = BookSchema()
books_schema = BookSchema(many=True)
Books = Books()

# Create a Book
@app.route('/book', methods=['POST'])
def add_book():
    isbn = request.json['name']
    title = request.json['title']
    author = request.json['author']
    date = request.json['date']

    new_book = Book(isbn, title, author, date)

    db.session.add(new_book)
    db.session.commit()

    return book_schema.jsonify(new_book)

# Get All Books
@app.route('/book', methods=['GET'])
def get_books():
    all_books = Book.query.all()
    result = books_schema.dump(all_books)
    return jsonify(result.data)

# Get sigle book
@app.route('/book/<id>', methods=['GET'])
def get_book(id):
    book = Book.query.get(id)
    return book_schema.jsonify(book)

# Update a book
@app.route('/book/<id>', methods=['PUT'])
def update_book(id):
    book = Book.query.get(id)

    isbn = request.json['isbn']
    title = request.json['title']
    author = request.json['author']
    date = request.json['date']

    book.isbn = isbn
    book.title = title
    book.author = author
    book.date = date

    db.session.commit()
    return book_schema.jsonify(book)

# Delete a book
@app.route('/book/<id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get(id)
    db.session.delete(book)
    db.session.commit()
    return book_schema.jsonify(book)

# Set index
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/list')
def list():
    return render_template('list.html', books = Books)

@app.route('/list/<string:id>')
def details(id):
    return render_template('details.html', id=id)

# Create a simple get request
@app.route('/remove', methods=['GET'])
def get():
    return jsonify({'msg': 'Hello world'})

# Run server
if __name__ == '__main__':
    app.run(debug=True)