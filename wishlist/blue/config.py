import os

DEBUG=True
BASEDIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'sqlite/db.wishlist')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY ='secret123'
