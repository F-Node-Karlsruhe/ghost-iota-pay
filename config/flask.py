
from os import getenv
from distutils.util import strtobool
from datetime import timedelta

SECRET_KEY = getenv('SECRET_KEY', None)

SQLALCHEMY_DATABASE_URI = getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:////app/data/db.sqlite3')

SQLALCHEMY_TRACK_MODIFICATIONS = bool(strtobool(getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'false')))

BASIC_AUTH_USERNAME = getenv('BASIC_AUTH_USERNAME', 'admin')

BASIC_AUTH_PASSWORD = getenv('BASIC_AUTH_PASSWORD', 'admin')

PERMANENT_SESSION_LIFETIME = timedelta(hours = int(getenv('MAX_SESSION_LIFETIME', 744)))