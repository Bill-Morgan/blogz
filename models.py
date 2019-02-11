from app import db
from datetime import datetime

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    post_txt = db.Column(db.String(1000))
    post_datetime = db.Column(db.TIMESTAMP,default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    def __init__(self, title, post_txt, owner):
        self.title = title
        self.post_txt = post_txt
        self.owner = owner
        
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username
