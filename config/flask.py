from os import getenv
from distutils.util import strtobool

SECRET_KEY = getenv('SECRET_KEY', None)

SQLALCHEMY_DATABASE_URI = getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///data/db.sqlite3')

SQLALCHEMY_TRACK_MODIFICATIONS = bool(strtobool(getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'false')))

BASIC_AUTH_USERNAME = getenv('ADMIN_USER', 'admin')

BASIC_AUTH_PASSWORD = getenv('ADMIN_PW', 'admin')
