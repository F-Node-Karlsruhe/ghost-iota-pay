
from os import getenv
from distutils.util import strtobool

SECRET_KEY = getenv('SECRET_KEY', None)

DATABASE_LOCATION = getenv('DATABASE_LOCATION', 'sqlite:///data/db.sqlite3')

SQLALCHEMY_TRACK_MODIFICATIONS = bool(strtobool(getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'false')))

BASIC_AUTH_USERNAME = getenv('BASIC_AUTH_USERNAME', 'admin')

BASIC_AUTH_PASSWORD = getenv('BASIC_AUTH_PASSWORD', 'admin')