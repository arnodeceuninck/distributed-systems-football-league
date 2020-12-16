import json
import unittest
from project.tests.base import BaseTestCase
from project import db
from project.api.models import Match, Division
from datetime import date, timedelta

def add_match(division_id, matchweek, time, home, away, date):
    match = Match(division_id=division_id, matchweek=matchweek, time=time, home=home, away=away, date=date)
    db.session.add(match)
    db.session.commit()
    return match

def add_division(name):
    division = Division(name=name)
    db.session.add(division)
    db.session.commit()
    return division

class TestMatcheservice(BaseTestCase):
    """Tests for the Matches Service."""

    def test_matches(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get('/matches/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_match(self):
        """Ensure a new match can be added to the database"""
        division = add_division("Cara pro leauge")
        with self.client:
            response = self.client.post(
                '/matches',
                data=json.dumps({
                    'division_id': division.id,
                    'matchweek': 1,
                    'time': '14:30:00',
                    "home": 42,
                    "away": 69,
                    'date': '1969-06-09'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn(' was added!', data['message'])
            self.assertIn('success', data['status'])

    def test_add_match_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty"""
        with self.client:
            response = self.client.post(
                '/matches',
                data=json.dumps({}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_match_invalid_json_keys(self):
        """Ensure error is thrown if the JSON object is empty"""
        with self.client:
            response = self.client.post(
                '/matches',
                data=json.dumps({'matchweek': 28}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_match(self):
        """Ensure get single match behaves correctly."""
        division = add_division("Cara pro leauge")
        match = add_match(division_id=division.id, matchweek=69, time="14:00:00", home=23, away=65, date="1943-12-31")
        with self.client:
            response = self.client.get(f'/matches/{match.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(23, data['data']['home'])
            self.assertEqual(65, data['data']['away'])
            self.assertIn('1943-12-31', data['data']['date'])
            self.assertIn('14:00:00', data['data']['time'])
            self.assertIn('success', data['status'])

    def test_single_match_no_id(self):
        """Ensure get single match behaves correctly."""
        with self.client:
            response = self.client.get(f'/matches/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Match does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_all_matches(self):
        """Ensure get single match behaves correctly."""
        division = add_division("Cara pro leauge")
        match = add_match(division_id=division.id, matchweek=69, time="14:00:00", home=23, away=65, date="1943-12-31")
        match = add_match(division_id=division.id, matchweek=69, time="14:00:00", home=23, away=65, date="1943-12-31")
        with self.client:
            response = self.client.get(f'/matches')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(2, len(data['data']['matches']))

    def test_recent(self):
        division = add_division("Cara pro leauge")
        today = date.today()
        match1 = add_match(division_id=division.id, matchweek=70, time="14:00:00", home=25, away=65, date=today + timedelta(days=5))
        match2 = add_match(division_id=division.id, matchweek=69, time="14:00:00", home=65, away=25, date=today + timedelta(days=1))
        match4 = add_match(division_id=division.id, matchweek=69, time="14:00:00", home=65, away=42, date=today - timedelta(days=4))
        other_division = add_division("Cara noob leauge")
        match3 = add_match(division_id=other_division.id, matchweek=70, time="14:00:00", home=25, away=65,
                           date=today - timedelta(weeks=2))
        match5 = add_match(division_id=other_division.id, matchweek=70, time="14:00:00", home=25, away=65,
                           date=today - timedelta(weeks=4))
        match6 = add_match(division_id=other_division.id, matchweek=70, time="14:00:00", home=25, away=65,
                           date=today - timedelta(weeks=3))
        with self.client:
            response = self.client.get(f'/matches/recent/65')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(3, len(data['data']['previous']))
            self.assertEqual(match4.id, data['data']['previous'][0]["id"])
            self.assertEqual(match3.id, data['data']['previous'][1]["id"])
            self.assertEqual(match6.id, data['data']['previous'][2]["id"])
            self.assertEqual(2, len(data['data']['upcoming']))
            self.assertEqual(match2.id, data['data']['upcoming'][0]["id"])
            self.assertEqual(match1.id, data['data']['upcoming'][1]["id"])

if __name__ == '__main__':
    unittest.main()
