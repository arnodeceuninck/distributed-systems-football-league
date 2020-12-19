from sqlalchemy.sql import func

from project import db
import enum
from sqlalchemy import func
import sys


class Division(db.Model):
    __tablename__ = "division"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    matches = db.relationship("Match", back_populates="division")

    def __init__(self, name, id=None):
        self.name = name
        if id is not None:
            self.id = id

    def to_json(self):
        return {"id": self.id, "name": self.name}

    def leauge_table(self):
        table = dict()
        for match in self.matches:
            if match.goals_home == None or match.goals_away == None:
                continue
            table.setdefault(match.home, {"wins": 0, "loses": 0, "ties": 0, "score": 0})
            table.setdefault(match.away, {"wins": 0, "loses": 0, "ties": 0, "score": 0})
            if match.goals_home > match.goals_away:
                table[match.home]["wins"] += 1
                table[match.away]["loses"] += 1
                table[match.home]["score"] += 3
            elif match.goals_home == match.goals_away:
                table[match.home]["ties"] += 1
                table[match.away]["ties"] += 1
                table[match.home]["score"] += 1
                table[match.away]["score"] += 1
            elif match.goals_home < match.goals_away:
                table[match.away]["wins"] += 1
                table[match.home]["loses"] += 1
                table[match.away]["score"] += 3
        return table

    def update(self, data):
        for key in data:
            try:
                value = data[key]
                if value == "None":
                    value = None
                setattr(self, key, value)
            except AttributeError:
                print(f"Warning:{key}, {data[key]} couldn't be added", file=sys.stderr)

class MatchStatus(db.Model):
    __tablename__ = "matchstatus"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)

    def __init__(self, name, id=None):
        self.name = name
        if id is not None:
            self.id = id

    def to_json(self):
        return {"id": self.id, "name": self.name}


class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    division_id = db.Column(db.Integer, db.ForeignKey("division.id"), nullable=False)
    division = db.relationship("Division", back_populates="matches")
    matchweek = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    home = db.Column(db.Integer, nullable=False)
    away = db.Column(db.Integer, nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('matchstatus.id'), nullable=True)
    status = db.relationship("MatchStatus")
    goals_home = db.Column(db.Integer, nullable=True)
    goals_away = db.Column(db.Integer, nullable=True)
    referee_id = db.Column(db.Integer, db.ForeignKey('referee.id'), nullable=True)
    referee = db.relationship("Referee", back_populates="matches")

    def __init__(self, division_id, matchweek, date, time, home, away, status_id=None, goals_home=None, goals_away=None,
                 id=None, referee_id=None):
        self.division_id = division_id
        self.matchweek = matchweek
        self.date = date
        self.time = time
        self.home = int(home)
        self.away = int(away)
        if referee_id is not None:
            self.referee_id = referee_id
        if status_id is not None and status_id is not "NULL":
            try:
                self.status_id = int(status_id)
            except ValueError:
                pass
        if goals_home is not None:
            try:
                self.goals_home = int(goals_home)
            except ValueError:
                pass
        if goals_away is not None:
            try:
                self.goals_away = int(goals_away)
            except ValueError:
                pass
        if id is not None:
            try:
                self.id = int(id)
            except ValueError:
                pass

    def to_json(self):
        return {"id": self.id, "division_id": self.division_id, "matchweek": self.matchweek, "date": self.date.strftime("%Y-%m-%d"),
                "time": self.time.strftime("%H:%M:%S"), "home": self.home, "away": self.away,
                "status_id": self.status_id, "goals_home": self.goals_home, "goals_away": self.goals_away, "referee_id": self.referee_id}

    def update(self, data):
        for key in data:
            try:
                value = data[key]
                if value == "None":
                    value = None
                setattr(self, key, value)
            except AttributeError:
                print(f"Warning:{key}, {data[key]} couldn't be added", file=sys.stderr)

class Referee(db.Model):
    __tablename__ = "referee"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=True)
    zip = db.Column(db.Integer, nullable=True)
    city = db.Column(db.String, nullable=True)
    phone = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    birthday = db.Column(db.Date, nullable=False)
    matches = db.relationship("Match", back_populates="referee")

    def __init__(self, firstname, lastname, birthday, address=None, zip=None, city=None, phone=None, email=None,
                 id=None):
        self.firstname = firstname
        self.lastname = lastname
        self.birthday = birthday
        if address is not None:
            self.address = address
        if zip is not None:
            self.zip = zip
        if city is not None:
            self.city = city
        if phone is not None:
            self.phone = phone
        if email is not None:
            self.email = email
        if id is not None:
            self.id = id

    def to_json(self):
        return {"id": self.id, "firstname": self.firstname, "lastname": self.lastname, "address": self.address,
                "zip": self.zip, "city": self.city, "phone": self.phone, "email": self.email, "birthday": self.birthday}

    def update(self, data):
        for key in data:
            try:
                value = data[key]
                if value == "None":
                    value = None
                setattr(self, key, value)
            except AttributeError:
                print(f"Warning:{key}, {data[key]} couldn't be added", file=sys.stderr)
