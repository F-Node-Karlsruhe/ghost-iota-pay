from database.db import db
from config import DEFAULT_IOTA_ADDRESS

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    iota_address = db.Column(db.String(64), default=DEFAULT_IOTA_ADDRESS)
