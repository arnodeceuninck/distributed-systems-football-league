from sqlalchemy.sql import func

from project import db
import enum

class Score:
    __tablename__ = 'scores'
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), primary_key=True)
    match = db.relationship("Match", back_populates="score")
    goals_home = db.Integer

class MatchStatus(enum.Enum):
    Postponed = 1
    Canceled = 2
    Forfait = 3

class Match:
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kickoff = db.Column(db.DateTime, nullable=True)
    home = db.Column(db.Integer, nullable=False)
    away = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(MatchStatus), nullable=True) # TODO: Specify enum valuesd
    score = db.relationship("Score", uselist=False, back_populates="match")

class Referee:
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=True)
    zip = db.Column(db.Integer, nullable=True)
    city = db.Column(db.String, nullable=True)
    phone = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    birthday = db.Column(db.Date, nullable=False)

