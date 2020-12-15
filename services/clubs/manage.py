from flask.cli import FlaskGroup
from project import create_app, db
from project.api.models import Club, Team
import unittest
import csv

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

def add_clubs():
    with open("data/clubs.csv") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count != 0:
                db.session.add(Club(stam_number=int(row[0]), name=row[1], address=row[2], zip=int(row[3]), city=row[4],
                                    website=row[5]))
                # print("club added")
            line_count += 1
    db.session.commit()

def add_teams():
    print("Adding Teams")
    with open("data/teams.csv") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count != 0:
                db.session.add(Team(id=int(row[0]), club_id=int(row[1]), suffix=row[2], outfit_colors=row[3]))
                # print("Team added")
            line_count += 1
    db.session.commit()


@cli.command()
def seed_db():
    """seeds the database."""
    add_clubs()
    add_teams()


if __name__ == '__main__':
    cli()
