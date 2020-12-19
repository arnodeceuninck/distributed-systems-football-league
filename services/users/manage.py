from flask.cli import FlaskGroup
from project import create_app, db
from project.api.models import User
import unittest

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

@cli.command()
def seed_db():
    """seeds the database."""
    db.session.add(User(username="admin", type="admin"))
    db.session.add(User(username="superadmin", type="superadmin"))

    for i in range(1, 50):
        db.session.add(User(username=f"user{i}", team_id=i))

    db.session.commit()

if __name__ == '__main__':
    cli()