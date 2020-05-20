from flask import Flask
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

# Init App
app = Flask(__name__)

# LOAD config file
app.config.from_pyfile('config.py')

# Import views/routes file
from views import *

# Init DB
db = SQLAlchemy(app)

#Init marshmallow
ma = Marshmallow(app) 

# Run server
if __name__ == '__main__':
    app.run()