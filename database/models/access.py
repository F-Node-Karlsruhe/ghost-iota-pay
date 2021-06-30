from database.db import db

class Access(db.Model):
    token_hash = db.Column(db.String(64), primary_key=True)
    slug = db.Column(db.String(128))
    slug_price = db.Column(db.Integer)
    exp_date = db.Column(db.DateTime)
