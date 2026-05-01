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

    # ---------- PAGE TEST ----------

    def test_car_registration_page_loads(self):
        response = self.client.get('/car_registration')
        self.assertEqual(response.status_code, 200)

    def test_car_registration_page_content(self):
        response = self.client.get('/car_registration')
        self.assertGreater(len(response.data), 0)

    def test_car_registration_content_type(self):
        response = self.client.get('/car_registration')
        self.assertIn('text/html', response.content_type)

    # ---------- API TESTS ----------

    def test_valid_car_registration(self):
        response = self.client.post(
            '/api/save_car_registration',
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

    def test_missing_make(self):
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
        data = self.valid_data.copy()
        data.pop('model')

        response = self.client.post(
            '/api/save_car_registration',
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

    def test_empty_fields(self):
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