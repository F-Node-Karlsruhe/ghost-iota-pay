from flask import Blueprint

view = Blueprint('main', __name__)

from . import routes, events