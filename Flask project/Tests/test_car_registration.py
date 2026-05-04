import unittest
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestCarRegistration(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        self.valid_data = {
            "make": "Toyota",
            "model": "Corolla",
            "year": "2025",
            "license": "ABC123",
            "engine": "V6",
            "wheels": "Alloy"
        }

    def _login(self):
        """Helper method to set up authenticated session"""
        with self.client:
            with self.client.session_transaction() as sess:
                sess['authenticated'] = True
                sess['email'] = 'test@example.com'
                sess['name'] = 'Test User'

    # ---------- PAGE TEST ----------

    def test_car_registration_page_loads(self):
        self._login()
        response = self.client.get('/car_registration')
        self.assertEqual(response.status_code, 200)

    def test_car_registration_page_content(self):
        self._login()
        response = self.client.get('/car_registration')
        self.assertGreater(len(response.data), 0)

    def test_car_registration_content_type(self):
        self._login()
        response = self.client.get('/car_registration')
        self.assertIn('text/html', response.content_type)

    # ---------- API TESTS ----------

    def test_valid_car_registration(self):
        self._login()
        response = self.client.post(
            '/api/save_car_registration',
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

    def test_missing_make(self):
        self._login()
        data = self.valid_data.copy()
        data.pop('make')

        response = self.client.post(
            '/api/save_car_registration',
            data=json.dumps(data),
            content_type='application/json'
        )

        # Still returns 200 because backend has no validation
        self.assertEqual(response.status_code, 200)

    def test_missing_model(self):
        self._login()
        data = self.valid_data.copy()
        data.pop('model')

        response = self.client.post(
            '/api/save_car_registration',
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

    def test_empty_fields(self):
        self._login()
        data = {
            "make": "",
            "model": "",
            "year": "",
            "license": "",
            "engine": "",
            "wheels": ""
        }

        response = self.client.post(
            '/api/save_car_registration',
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()