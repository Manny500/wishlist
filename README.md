Wish List Design Doc
Developing a Digital Management System

Abstract
The ask was to create a REST API in python3 that gives users the ability to manage their own book wishlist. The API would handle add, update, and delete, of the users books. These updates would then be made persistent with the use a of database.

Technologies
- python3
- pip3
- flask
- sqlalchemy
- marshmallow
- wtforms
- requests
- visual studio code
- terminal 
- chrome

API
login(email, password) POST
This allows the client to authenticate the application by checking its credentials again the database.

register(firstName, lastName, email, password) POST
This allows the user to register to the application by and saved the information in the database.

book(id) GET
Will retrieve the one book which matches that particular id.

book(user) GET
Will retrieve all the books that the user currently has.

book(id) DELETE
Will delete the specific book

book(id, title, author, isbn, date) PUT
Will update the specific book