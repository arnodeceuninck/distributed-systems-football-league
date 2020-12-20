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

    def test_teams(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get('/teams/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    # def test_add_team(self):
    #     """Ensure a new team can be added to the database"""
    #     club = add_club(stam_number=234, name="De voetballers", address="Heystraat 32", zip=4233, city="Antwerpen")
    #     with self.client:
    #         response = self.client.post(
    #             '/teams',
    #             data=json.dumps({
    #                 'stam_number': club.stam_number,
    #                 'outfit_colors': "Zwart/Oranje",
    #                 'suffix': "B"
    #             }),
    #             content_type='application/json',
    #         )
    #         data = json.loads(response.data.decode())
    #         self.assertEqual(response.status_code, 201)
    #         self.assertIn(' was added!', data['message'])
    #         self.assertIn('success', data['status'])

    def test_add_team_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty"""
        with self.client:
            response = self.client.post(
                '/teams',
                data=json.dumps({}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_team_invalid_json_keys(self):
        """Ensure error is thrown if the JSON object is empty"""
        club = add_club(stam_number=234, name="De voetballers", address="Heystraat 32", zip=4233, city="Antwerpen")
        with self.client:
            response = self.client.post(
                '/teams',
                data=json.dumps({
                    'outfit_colors': "Zwart/Oranje",
                    'suffix': "B"
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_nonexisting_club(self):
        """Ensure a team can't be added if the club doesn't exist"""
        with self.client:
            response = self.client.post(
                '/teams',
                data=json.dumps({
                    'club_id': 234,
                    'outfit_colors': "Zwart/Oranje",
                    'suffix': "B"
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_multiple_teams_to_club(self):
        """Ensure multiple teams can be added to a club"""
        club = add_club(stam_number=234, name="De voetballers", address="Heystraat 32", zip=4233, city="Antwerpen")
        with self.client:
            response = self.client.post(
                '/teams',
                data=json.dumps({
                    'club_id': club.stam_number,
                    'outfit_colors': "Zwart/Oranje",
                    'suffix': "B"
                }),
                content_type='application/json',
            )
            response = self.client.post(
                '/teams',
                data=json.dumps({
                    'club_id': club.stam_number,
                    'outfit_colors': "Okergeel/Bordeauxrood",
                    'suffix': "A"
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn(' was added!', data['message'])
            self.assertIn('success', data['status'])

    def test_single_team(self):
        """Ensure get single team behaves correctly."""
        club = add_club(stam_number=234, name="De voetballers", address="Heystraat 32", zip=4233, city="Antwerpen")
        team = add_team(club_id=club.stam_number, colors="Zwart/Oranje", suffix="B")
        with self.client:
            response = self.client.get(f'/teams/{team.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(234, int(data['data']['club_id']))
            self.assertIn("Zwart/Oranje", data['data']['outfit_colors'])
            self.assertEqual(team.id, int(data['data']['id']))
            self.assertIn("B", data['data']['suffix'])
            self.assertIn('success', data['status'])

    def test_single_team_no_id(self):
        """Ensure get single team behaves correctly."""
        with self.client:
            response = self.client.get(f'/teams/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('team does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_all_teams(self):
        """Ensure get single team behaves correctly."""
        club = add_club(stam_number=234, name="De voetballers", address="Heystraat 32", zip=4233, city="Antwerpen")
        team = add_team(club_id=club.stam_number, colors="Zwart/Oranje", suffix="B")
        club = add_club(stam_number=235, name="De balvoeters", address="Heystraat 32", zip=4233, city="Antwerpen")
        team = add_team(club_id=club.stam_number, colors="Okergeel/Bordeauxrood", suffix="C")
        with self.client:
            response = self.client.get(f'/teams')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(234, int(data['data']['teams'][0]['club_id']))
            self.assertIn("Zwart/Oranje", data['data']['teams'][0]['outfit_colors'])
            self.assertIn("B", data['data']['teams'][0]['suffix'])
            self.assertEqual(235, int(data['data']['teams'][1]['club_id']))
            self.assertIn("Okergeel/Bordeauxrood", data['data']['teams'][1]['outfit_colors'])
            self.assertIn("C", data['data']['teams'][1]['suffix'])


if __name__ == '__main__':
    unittest.main()
