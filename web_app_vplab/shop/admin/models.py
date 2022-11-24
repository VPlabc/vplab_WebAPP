from shop import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50),unique=False, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(180),unique=False, nullable=False)
    profile = db.Column(db.String(180), unique=False, nullable=False,default='profile.jpg')

    def __repr__(self):
        return '<User %r>' % self.username


class Calendar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    url = db.Column(db.Numeric(10,2), nullable=False)
    Class = db.Column(db.Integer, default=0)
    start_date = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
