import json
import unittest
from project.tests.base import BaseTestCase
from project import db
from project.api.models import Referee

def add_referee(firstname, lastname, birthday):
    referee = Referee(firstname=firstname, lastname=lastname, birthday=birthday)
    db.session.add(referee)
    db.session.commit()
    return referee

class TestRefereeService(BaseTestCase):
    """Tests for the Referees Service."""

    def test_referees(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get('/referees/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_referee(self):
        """Ensure a new referee can be added to the database"""
        with self.client:
            response = self.client.post(
                '/referees',
                data=json.dumps({
                    'firstname': 'Joske',
                    'lastname': 'Vermeulen',
                    'birthday': '1969-06-09'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('Joske Vermeulen was added!', data['message'])
            self.assertIn('success', data['status'])

    def test_add_referee_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty"""
        with self.client:
            response = self.client.post(
                '/referees',
                data=json.dumps({}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_referee_invalid_json_keys(self):
        """Ensure error is thrown if the JSON object is empty"""
        with self.client:
            response = self.client.post(
                '/referees',
                data=json.dumps({'firstname': 'Joske'}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_referee(self):
        """Ensure get single referee behaves correctly."""
        referee = add_referee(firstname="Joske", lastname="Vermeulen", birthday="1997-10-03")
        with self.client:
            response = self.client.get(f'/referees/{referee.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('Joske', data['data']['firstname'])
            self.assertIn('Vermeulen', data['data']['lastname'])
            self.assertIn('success', data['status'])

    def test_single_referee_no_id(self):
        """Ensure get single referee behaves correctly."""
        with self.client:
            response = self.client.get(f'/referees/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Referee does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_all_referees(self):
        """Ensure get single referee behaves correctly."""
        add_referee(firstname="michael", lastname="achternaam", birthday="1964-02-23")
        add_referee(firstname="bob", lastname="yolo", birthday="1964-02-23")
        with self.client:
            response = self.client.get(f'/referees')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('michael', data['data']['referees'][0]['firstname'])
            self.assertIn('achternaam', data['data']['referees'][0]['lastname'])
            self.assertIn('bob', data['data']['referees'][1]['firstname'])
            self.assertIn('yolo', data['data']['referees'][1]['lastname'])

if __name__ == '__main__':
    unittest.main()
