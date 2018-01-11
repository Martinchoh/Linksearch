from sqlalchemy import Integer, String, DateTime
from database import db
from datetime import datetime

notifications_per_users = db.Table('notifications_per_users',
                                   db.Column('notifications_id', db.Integer, db.ForeignKey('notifications.id')),
                                   db.Column('users_id', db.Integer, db.ForeignKey('users.id')))


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(Integer, primary_key=True)
    email = db.Column(String(), unique=True, nullable=False)
    password = db.Column(String(), nullable=False)
    name = db.Column(String(), nullable=False)
    last_name = db.Column(String(), nullable=False)
    birth_day = db.Column(DateTime(), nullable=True)
    country = db.Column(String(), nullable=False)
    City = db.Column(String(), nullable=False)
    role = db.Column(String(), nullable=False)
    fcm_token = db.Column(String(), nullable=True)
    notifications = db.relationship("Notification", secondary=notifications_per_users, uselist=True)

    def __init__(self, name=None, password=None, birth_day=None, email=None, role=None, country=None, city=None,
                 last_name=None):
        self.name = name
        self.last_name = last_name
        self.password = password
        self.birth_day = birth_day
        self.country = country
        self.city = city
        self.email = email
        self.role = role


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(Integer, primary_key=True)
    title = db.Column(String(), nullable=False)
    message = db.Column(String(), nullable=False)
    datetime = db.Column(DateTime, nullable=False)
    users = db.relationship("User", secondary=notifications_per_users,
                            cascade="save-update, merge", uselist=True)

    def __init__(self, title, message):
        self.title = title
        self.message = message
        self.datetime = datetime.now()


class Messages(db.Model):
    __tablename__ = 'messages'
    id = db.Column(Integer(), primary_key=True)
    message = db.Column(String(), nullable=False)
    send_time = db.Column(DateTime(), nullable=False)

    def __init__(self, message=None, send_time= None):
        self.message = message
        self.send_time = send_time
