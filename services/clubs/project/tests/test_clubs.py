import json
import unittest
from project.tests.base import BaseTestCase
from project import db
from project.api.models import Team, Club

def add_team(club_id, colors, suffix=None):
    team = Team(club_id=club_id, outfit_colors=colors, suffix=suffix)
    db.session.add(team)
    db.session.commit()
    return team

def add_club(stam_number, name, address, zip, city, website=None):
    club = Club(stam_number=stam_number, name=name, address=address, zip=zip, city=city, website=website)
    db.session.add(club)
    db.session.commit()
    return club

class TestClubService(BaseTestCase):
    """Tests for the clubs Service."""

    def test_clubs(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get('/clubs/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_club(self):
        """Ensure a new club can be added to the database"""
        with self.client:
            response = self.client.post(
                '/clubs',
                data=json.dumps({
                    'stam_number': 420,
                    'name': "De voetbal jochies",
                    'address': "Middelheimlaan 1",
                    "zip": 2020,
                    "city": "Antwerpen",
                    'website': 'voetbal.com'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('420 was added!', data['message'])
            self.assertIn('success', data['status'])

    def test_add_club_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty"""
        with self.client:
            response = self.client.post(
                '/clubs',
                data=json.dumps({}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_club_invalid_json_keys(self):
        """Ensure error is thrown if the JSON object is empty"""
        with self.client:
            response = self.client.post(
                '/clubs',
                data=json.dumps({
                    'stam_number': 420,
                    'address': "Middelheimlaan 1",
                    "zip": 2020,
                    "city": "Antwerpen",
                    'website': 'voetbal.com'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_club_duplicate_stam_number(self):
        """Ensure a new club can be added to the database"""
        with self.client:
            response = self.client.post(
                '/clubs',
                data=json.dumps({
                    'stam_number': 420,
                    'name': "De voetbal jochies",
                    'address': "Middelheimlaan 1",
                    "zip": 2020,
                    "city": "Antwerpen",
                    'website': 'voetbal.com'
                }),
                content_type='application/json',
            )
            response = self.client.post(
                '/clubs',
                data=json.dumps({
                    'stam_number': 420,
                    'name': "De voetbal jochies",
                    'address': "Middelheimlaan 1",
                    "zip": 2020,
                    "city": "Antwerpen",
                    'website': 'voetbal.com'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Sorry. That stam number already exists.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_club(self):
        """Ensure get single club behaves correctly."""
        club = add_club(stam_number=234, name="De voetballers", address="Heystraat 32", zip=4233, city="Antwerpen")
        with self.client:
            response = self.client.get(f'/clubs/{club.stam_number}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(234, int(data['data']['stam_number']))
            self.assertIn("De voetballers", data['data']['name'])
            self.assertIn("Heystraat 32", data['data']['address'])
            self.assertEqual(4233, int(data['data']['zip']))
            self.assertIn("Antwerpen", data['data']['city'])
            self.assertIn('success', data['status'])

    def test_single_club_no_id(self):
        """Ensure get single club behaves correctly."""
        with self.client:
            response = self.client.get(f'/clubs/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('club does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_all_clubs(self):
        """Ensure get single club behaves correctly."""
        club = add_club(stam_number=234, name="De voetballers", address="Heystraat 32", zip=4233, city="Antwerpen")
        club = add_club(stam_number=235, name="De balvoeters", address="Hallostraat 32", zip=2333, city="Borsbeek")
        with self.client:
            response = self.client.get(f'/clubs')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(234, int(data['data']['clubs'][0]['stam_number']))
            self.assertIn("De voetballers", data['data']['clubs'][0]['name'])
            self.assertEqual(235, int(data['data']['clubs'][1]['stam_number']))
            self.assertIn("De balvoeters", data['data']['clubs'][1]['name'])

    def test_all_teams_from_club(self):
        """Ensure get single team behaves correctly."""
        club = add_club(stam_number=234, name="De voetballers", address="Heystraat 32", zip=4233, city="Antwerpen")
        team = add_team(club_id=club.stam_number, colors="Zwart/Oranje", suffix="B")
        team = add_team(club_id=club.stam_number, colors="Okergeel/Bordeauxrood", suffix="C")

        # Team that shouldn't be in the output
        other_club = add_club(stam_number=235, name="De balvoeters", address="Heystraat 32", zip=4233, city="Antwerpen")
        team = add_team(club_id=other_club.stam_number, colors="Appelblauwzeegroen", suffix="A")

        with self.client:
            response = self.client.get(f'/clubs/{club.stam_number}/teams')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(2, len(data['data']['teams']))
            self.assertEqual(234, int(data['data']['teams'][0]['club_id']))
            self.assertIn("Zwart/Oranje", data['data']['teams'][0]['outfit_colors'])
            self.assertIn("B", data['data']['teams'][0]['suffix'])
            self.assertEqual(234, int(data['data']['teams'][1]['club_id']))
            self.assertIn("Okergeel/Bordeauxrood", data['data']['teams'][1]['outfit_colors'])
            self.assertIn("C", data['data']['teams'][1]['suffix'])


if __name__ == '__main__':
    unittest.main()
