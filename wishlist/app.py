from flask import Flask, render_template
from data import Books

app = Flask(__name__)

Books = Books()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/books')
def books():
    return render_template('books.html', books = Books)

@app.route('/book/<string:id>')
def book(id):
    return render_template('book.html', id = id)

if __name__ == '__main__':
    app.run(debug=True)