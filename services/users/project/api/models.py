from sqlalchemy.sql import func

from project import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    team_id = db.Column(db.Integer, nullable=True)

    def __init__(self, username, email, password="password"):
        self.username = username
        self.email = email
        self.password = password # Hashing passwords is out of the scope of this course

    def to_json(self):
        return {'id': self.id, 'username': self.username, 'email': self.email}