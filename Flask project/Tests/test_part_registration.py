import unittest
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestPartRegistration(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        with self.client.session_transaction() as session:
            session['authenticated'] = True
            session['email'] = 'test@example.com'
            session['name'] = 'Test User'

        self.valid_data = {
            'brand': 'Test Brand',
            'year': '2026',
            'name': 'Test Part',
            'part_name': 'Test Part',
            'price': '100.00',
            'description': 'Test description',
            'image': 'test.jpg'
        }

    # ---------- PAGE TESTS ----------

    def test_page_loads(self):
        response = self.client.get('/part_registration')
        self.assertEqual(response.status_code, 200)

    def test_page_has_content(self):
        response = self.client.get('/part_registration')
        self.assertGreater(len(response.data), 0)

    def test_page_content_type(self):
        response = self.client.get('/part_registration')
        self.assertIn('text/html', response.content_type)

    # ---------- API TESTS ----------

    def test_valid_part_registration(self):
        response = self.client.post(
            '/api/save_part_registration',
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )

        # SUCCESS should return 201
        self.assertEqual(response.status_code, 201)

    def test_missing_name(self):
        data = self.valid_data.copy()
        data.pop('name')

        response = self.client.post(
            '/api/save_part_registration',
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

    def test_missing_price(self):
        data = self.valid_data.copy()
        data.pop('price')

        response = self.client.post(
            '/api/save_part_registration',
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

    def test_missing_description(self):
        data = self.valid_data.copy()
        data.pop('description')

        response = self.client.post(
            '/api/save_part_registration',
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

    def test_missing_image(self):
        data = self.valid_data.copy()
        data.pop('image')

        response = self.client.post(
            '/api/save_part_registration',
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

    def test_invalid_price(self):
        data = self.valid_data.copy()
        data['price'] = "invalid"

        response = self.client.post(
            '/api/save_part_registration',
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()