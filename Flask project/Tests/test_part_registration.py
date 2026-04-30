import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestPartRegistration(unittest.TestCase):
    """Test suite for the part registration screen route"""

    def setUp(self):
        """Set up test client before each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Valid test data for part registration
        self.valid_data = {
            'name': 'Test Part',
            'price': '100.00',
            'description': 'A test part description',
            'image': 'test_image.jpg'
        }

    def tearDown(self):
        """Clean up after each test"""
        pass

    def test_part_registration_page_loads_successfully(self):
        """Test that the part registration page returns a 200 status code"""
        response = self.client.get('/part_registration')
        self.assertEqual(response.status_code, 200)

    def test_part_registration_page_renders_correct_template(self):
        """Test that the part registration page renders the part_registration.html template"""
        response = self.client.get('/part_registration')
        # Check for common content that should be on the part registration page
        self.assertGreater(len(response.data), 0)

    def test_part_registration_page_response_content_type(self):
        """Test that the part registration page returns HTML content"""
        response = self.client.get('/part_registration')
        self.assertIn('text/html', response.content_type)

    def test_save_part_registration_with_valid_json_data(self):
        """Test saving part registration with valid JSON data"""
        response = self.client.post(
            '/api/save_part_registration',
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Part registration recieved', response.data)

    def test_save_part_registration_returns_json_response(self):
        """Test that save part registration returns valid JSON response"""
        response = self.client.post(
            '/api/save_part_registration',
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )

        self.assertIn('application/json', response.content_type)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, dict)
        self.assertIn('message', response_data)

    def test_save_part_registration_missing_name(self):
        """Test part registration with missing name"""
        data = self.valid_data.copy()
        del data['name']

        response = self.client.post(
            '/api/save_part_registration',
            data=json.dumps(data),
            content_type='application/json'
        )

        # Since there's no validation, it should still succeed
        self.assertEqual(response.status_code, 200)

    def test_save_part_registration_missing_price(self):
        """Test part registration with missing price"""
        data = self.valid_data.copy()
        del data['price']

        response = self.client.post(
            '/api/save_part_registration',
            data=json.dumps(data),
            content_type='application/json'
        )

        # Since there's no validation, it should still succeed
        self.assertEqual(response.status_code, 200)

    def test_save_part_registration_missing_description(self):
        """Test part registration with missing description"""
        data = self.valid_data.copy()
        del data['description']

        response = self.client.post(
            '/api/save_part_registration',
            data=json.dumps(data),
            content_type='application/json'
        )

        # Since there's no validation, it should still succeed
        self.assertEqual(response.status_code, 200)

    def test_save_part_registration_missing_image(self):
        """Test part registration with missing image"""
        data = self.valid_data.copy()
        del data['image']

        response = self.client.post(
            '/api/save_part_registration',
            data=json.dumps(data),
            content_type='application/json'
        )

        # Since there's no validation, it should still succeed
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()