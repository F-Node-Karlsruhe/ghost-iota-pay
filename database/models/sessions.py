from database.db import db
from datetime import datetime

class Session(db.Model):
    token_hash = db.Column(db.String(64), primary_key=True)
    session_id = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)