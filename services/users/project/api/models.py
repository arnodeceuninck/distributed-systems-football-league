from sqlalchemy.sql import func
import sys
from project import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False) # Ah yes, plain text passwords
    team_id = db.Column(db.Integer, nullable=True)
    type = db.Column(db.String(128), nullable=False)

    def __init__(self, username, password="password", type="user", team_id=-1):
        if type is None:
            type = "user"
        assert type in ["user", "admin", "superadmin"]

        if password is None:
            password = "password"

        if team_id is None:
            team_id = -1

        self.type = type
        self.username = username
        self.password = password # Hashing passwords is out of the scope of this course
        self.team_id = team_id

    def to_json(self):
        return {'id': self.id, 'username': self.username, 'password': self.password, 'team_id': self.team_id, 'type': self.type}

    def update(self, data):
        for key in data:
            try:
                value = data[key]
                if value == "None":
                    value = None
                setattr(self, key, value)
            except AttributeError:
                print(f"Warning:{key}, {data[key]} couldn't be added", file=sys.stderr)