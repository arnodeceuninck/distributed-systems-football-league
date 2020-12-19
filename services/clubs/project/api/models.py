from sqlalchemy.sql import func
import sys
from project import db

class Club(db.Model):
    __tablename__ = 'clubs'
    stam_number = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    zip = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    website = db.Column(db.String, nullable=True)
    teams = db.relationship("Team", back_populates='club')

    def __init__(self, stam_number: int, name: str, address: str, zip: int, city: str, website=None):
        if stam_number is not None:
            self.stam_number = stam_number
        self.name = name
        self.address = address
        self.zip = zip
        self.city = city
        self.website = website

    def to_json(self):
        return {"stam_number": self.stam_number, "name": self.name, "address": self.address, "zip": self.zip, "city": self.city, "website": self.website}

    def update(self, data):
        for key in data:
            try:
                value = data[key]
                if value == "None":
                    value = None
                setattr(self, key, value)
            except AttributeError:
                print(f"Warning:{key}, {data[key]} couldn't be added", file=sys.stderr)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.stam_number'), nullable=False)
    club = db.relationship("Club", back_populates="teams")
    outfit_colors = db.Column(db.String, nullable=True)
    suffix = db.Column(db.String, nullable=True)

    def __init__(self, club_id: int, outfit_colors: str, suffix: str=None, id: int=None):
        self.club_id = club_id
        if outfit_colors is not None:
            self.outfit_colors = outfit_colors
        if suffix is not None:
            self.suffix = suffix
        if id is not None:
            self.id = id

    def to_json(self):
        return {"id": self.id, "club_id": self.club_id, "outfit_colors": self.outfit_colors, "suffix": self.suffix}

    def update(self, data):
        for key in data:
            try:
                value = data[key]
                if value == "None":
                    value = None
                setattr(self, key, value)
            except AttributeError:
                print(f"Warning:{key}, {data[key]} couldn't be added", file=sys.stderr)

