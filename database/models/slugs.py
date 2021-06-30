from database.db import db
from config import DEFAULT_PRICE

class Slug(db.Model):
    slug = db.Column(db.String(128), primary_key=True)
    author_id = db.Column(db.Integer)
    price = db.Column(db.Integer, default=DEFAULT_PRICE)

