from sqlalchemy.sql import func

from project import db

class Club(db.Model):
    __tablename__ = 'clubs'
    stam_number = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=True)
    address = db.Column(db.String, nullable=False)
    zip = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    website = db.Column(db.String, nullable=True)

class Team(db.Model):
    outfit_colors = db.Column(db.String, nullable=True)
    suffix = db.Column(db.String, nullable=True)
