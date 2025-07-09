# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    avatar = db.Column(db.String(200), nullable=True)  # Path to avatar image
    announcements = db.relationship('Announcement', backref='author', lazy=True)
    marketplace_posts = db.relationship('Marketplace', backref='author', lazy=True)
    services = db.relationship('Service', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(20))  # Announcements, General, MM Service
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.String(20))

class Marketplace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(20))  # Buyers, Sellers
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price = db.Column(db.String(20))
    date = db.Column(db.String(20))

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(20))  # Buy, Sell
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price = db.Column(db.String(20))
    date = db.Column(db.String(20))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_type = db.Column(db.String(20))  # announcement, marketplace, service
    post_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text)
    date = db.Column(db.String(20))