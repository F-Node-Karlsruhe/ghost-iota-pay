from database.db import db
from datetime import datetime, timedelta
from config import SESSION_LIFETIME

class Access(db.Model):
    token_hash = db.Column(db.String(64), primary_key=True)
    exp_date = db.Column(db.DateTime, default=datetime.utcnow() + timedelta(hours = SESSION_LIFETIME))