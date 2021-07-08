from database.db import db
from config.settings import DEFAULT_IOTA_ADDRESS

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    iota_address = db.Column(db.String(64), default=DEFAULT_IOTA_ADDRESS)
