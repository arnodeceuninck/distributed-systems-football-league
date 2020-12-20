import json
import unittest
from project.tests.base import BaseTestCase
from project import db
from project.api.models import Match, Division

def add_match(division_id, matchweek, time, home, away, date, goals_home=None, goals_away=None):
    match = Match(division_id=division_id, matchweek=matchweek, time=time, home=home, away=away, date=date, goals_home=goals_home, goals_away=goals_away)
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
        response = self.client.get('/divisions/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_matches(self):
        """Ensure new matches can be added to the database"""
        division = add_division("Cara pro leauge")
        match = add_match(division_id=division.id, matchweek=70, time="14:00:00", home=25, away=65, date="1943-12-23", goals_home=0, goals_away=1)
        match = add_match(division_id=division.id, matchweek=69, time="14:00:00", home=23, away=65, date="1943-12-31", goals_home=1, goals_away=6)
        with self.client:
            response = self.client.get(f'/matches')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(2, len(data['data']['matches']))
            self.assertEqual(division.id, data['data']['matches'][0]["division_id"])
            self.assertEqual(division.id, data['data']['matches'][1]["division_id"])

    def test_leauge_table(self):
        """Ensure new matches can be added to the database"""
        division = add_division("Cara pro leauge")
        match = add_match(division_id=division.id, matchweek=70, time="14:00:00", home=25, away=65, date="1943-12-23", goals_home=0, goals_away=1)
        match = add_match(division_id=division.id, matchweek=69, time="14:00:00", home=65, away=25, date="1943-12-31", goals_home=1, goals_away=6)
        with self.client:
            response = self.client.get(f'/divisions/{division.id}/league_table')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            # self.assertEqual("False", data['data']['league'])
            self.assertEqual(1, data['data']['league']["25"]["wins"])
            self.assertEqual(1, data['data']['league']["25"]["loses"])
            self.assertEqual(0, data['data']['league']["25"]["ties"])
            self.assertEqual(3, data['data']['league']["25"]["score"])
            self.assertEqual(1, data['data']['league']["65"]["wins"])
            self.assertEqual(3, data['data']['league']["65"]["score"])

    def test_fixtures(self):
        division = add_division("Cara pro leauge")
        match1 = add_match(division_id=division.id, matchweek=70, time="14:00:00", home=25, away=65, date="1943-12-23", goals_home=0, goals_away=1)
        match2 = add_match(division_id=division.id, matchweek=69, time="14:00:00", home=65, away=25, date="1943-12-31", goals_home=1, goals_away=6)
        other_division = add_division("Cara noob leauge")
        match3 = add_match(division_id=other_division.id, matchweek=70, time="14:00:00", home=25, away=65, date="1943-12-23", goals_home=0, goals_away=1)
        with self.client:
            response = self.client.get(f'/divisions/{division.id}/fixtures')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(2, len(data['data']['fixtures']))
            self.assertEqual(match1.id, data['data']['fixtures'][0]["id"])
            self.assertEqual(match2.id, data['data']['fixtures'][1]["id"])

    def test_fixtures_for_team(self):
        division = add_division("Cara pro leauge")
        match1 = add_match(division_id=division.id, matchweek=70, time="14:00:00", home=25, away=65, date="1943-12-23", goals_home=0, goals_away=1)
        match2 = add_match(division_id=division.id, matchweek=69, time="14:00:00", home=65, away=25, date="1943-12-31", goals_home=1, goals_away=6)
        match4 = add_match(division_id=division.id, matchweek=69, time="14:00:00", home=22, away=42, date="1943-12-31", goals_home=1, goals_away=6)
        other_division = add_division("Cara noob leauge")
        match3 = add_match(division_id=other_division.id, matchweek=70, time="14:00:00", home=25, away=65, date="1943-12-23", goals_home=0, goals_away=1)
        with self.client:
            response = self.client.get(f'/divisions/{division.id}/fixtures/25')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(2, len(data['data']['fixtures']))
            self.assertEqual(match1.id, data['data']['fixtures'][0]["id"])
            self.assertEqual(match2.id, data['data']['fixtures'][1]["id"])

    def test_stats(self):
        division = add_division("Cara pro leauge")
        match1 = add_match(division_id=division.id, matchweek=70, time="14:00:00", home=25, away=65, date="1943-12-23", goals_home=0, goals_away=1)
        match2 = add_match(division_id=division.id, matchweek=69, time="14:00:00", home=65, away=25, date="1943-12-31", goals_home=1, goals_away=6)
        match4 = add_match(division_id=division.id, matchweek=69, time="14:00:00", home=25, away=42, date="1943-12-31", goals_home=1, goals_away=0)
        other_division = add_division("Cara noob leauge")
        match3 = add_match(division_id=other_division.id, matchweek=70, time="14:00:00", home=25, away=65, date="1943-12-23", goals_home=0, goals_away=200)
        with self.client:
            response = self.client.get(f'/divisions/{division.id}/stats')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(25, data['data']['best_attack']["team"])
            self.assertEqual(7, data['data']['best_attack']["count"])
            self.assertEqual(42, data['data']['best_defense']["team"])
            self.assertEqual(1, data['data']['best_defense']["count"])
            self.assertEqual(65, data['data']['most_clean_sheets']["team"])
            self.assertEqual(1, data['data']['most_clean_sheets']["count"])

if __name__ == '__main__':
    unittest.main()
