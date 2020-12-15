from flask.cli import FlaskGroup
from project import create_app, db
import unittest
import csv
from project.api.models import MatchStatus, Referee, Match, Division

app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command()
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command()
def test():
    """Runs the tests without code coverage"""
    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


def add_status():
    with open("data/status.csv") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count != 0:
                db.session.add(MatchStatus(id=row[0], name=row[1]))
                # print("club added")
            line_count += 1
    db.session.commit()


def add_divisions():
    with open("data/divisions.csv") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count != 0:
                db.session.add(Division(id=row[0], name=row[1]))
                # print("club added")
            line_count += 1
    db.session.commit()


def add_matches(filename):
    with open(filename) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count != 0:
                db.session.add(
                    Match(division_id=row[0], matchweek=row[1], date=row[2], time=row[3], home=row[4], away=row[5],
                          goals_home=row[6], goals_away=row[7], status_id=row[8]))
                # print("club added")
            line_count += 1
    db.session.commit()

def add_referees():
    with open("data/referees.csv") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count != 0:
                db.session.add(Referee(firstname=row[0], lastname=row[1], address=row[2], zip=row[3], city=row[4], phone=row[5], email=row[6], birthday=row[7]))
                # print("club added")
            line_count += 1
    db.session.commit()


@cli.command()
def seed_db():
    """seeds the database."""
    add_status()
    add_divisions()
    add_matches("data/matches_2018_2019.csv")
    add_matches("data/matches_2019_2020.csv")
    add_matches("data/matches_2020_2021.csv")
    add_referees()


if __name__ == '__main__':
    cli()
