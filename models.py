from database import db
from datetime import datetime, timezone
from sqlalchemy import text

class User(db.Model):
    __tablename__ = 'users'
    """Keeps track of the user data and their cash"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    hash = db.Column(db.String(256), nullable=False)
    cash = db.Column(db.Float, nullable=False, server_default=text("10000.00"))

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Buy(db.Model):
    __tablename__ = 'transactions'
    """Originally, was supposed to only track buys, but I suppose a better name now would have been Transaction"""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    symbol = db.Column(db.String(5), nullable=False)
    shares = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return '<Buy {}>'.format(self.id)
