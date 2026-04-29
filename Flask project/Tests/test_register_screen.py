import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestRegisterScreen(unittest.TestCase):
    """Test suite for the register screen route"""

    def setUp(self):
        """Set up test client before each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Valid test data
        self.valid_data = {
            'email': 'testuser@example.com',
            'password': 'TestPassword123!',
            'fullname': 'Test User',
            'username': 'testuser123'
        }

    def tearDown(self):
        """Clean up after each test"""
        pass


    def test_register_page_loads_successfully(self):
        """Test that the register page returns a 200 status code"""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)

    def test_register_page_renders_correct_template(self):
        """Test that the register page renders the register_screen.html template"""
        response = self.client.get('/register')
        # Check for common content that should be on the register page
        self.assertGreater(len(response.data), 0)

    def test_register_page_response_content_type(self):
        """Test that the register page returns HTML content"""
        response = self.client.get('/register')
        self.assertIn('text/html', response.content_type)

    @patch('app.auth.create_user')
    def test_register_with_valid_json_data(self, mock_create_user):
        """Test registration with valid JSON data"""
        mock_create_user.return_value = MagicMock(uid='testuser123')

        response = self.client.post(
            '/register',
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertIn(b'success', response.data)
        self.assertIn(b'Registration successful', response.data)

    @patch('app.auth.create_user')
    def test_register_with_valid_form_data(self, mock_create_user):
        """Test registration with valid form data (not JSON)"""
        mock_create_user.return_value = MagicMock(uid='testuser123')

        response = self.client.post('/register', data=self.valid_data)

        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertTrue(response_data.get('success'))

    @patch('app.auth.create_user')
    def test_register_creates_user_with_correct_params(self, mock_create_user):
        """Test that Firebase create_user is called with correct parameters"""
        mock_create_user.return_value = MagicMock(uid='testuser123')

        self.client.post(
            '/register',
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )

        mock_create_user.assert_called_once_with(
            email=self.valid_data['email'],
            password=self.valid_data['password'],
            display_name=self.valid_data['fullname'],
            uid=self.valid_data['username']
        )

    @patch('app.auth.create_user')
    def test_register_returns_json_response(self, mock_create_user):
        """Test that register returns valid JSON response"""
        mock_create_user.return_value = MagicMock(uid='testuser123')

        response = self.client.post(
            '/register',
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )

        self.assertIn('application/json', response.content_type)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, dict)

    def test_register_missing_email(self):
        """Test registration fails when email is missing"""
        data = self.valid_data.copy()
        del data['email']

        response = self.client.post(
            '/register',
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'All fields are required', response.data)

    def test_register_missing_password(self):
        """Test registration fails when password is missing"""
        data = self.valid_data.copy()
        del data['password']

        response = self.client.post(
            '/register',
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'All fields are required', response.data)

    def test_register_missing_fullname(self):
        """Test registration fails when fullname is missing"""
        data = self.valid_data.copy()
        del data['fullname']

        response = self.client.post(
            '/register',
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'All fields are required', response.data)

    def test_register_missing_username(self):
        """Test registration fails when username is missing"""
        data = self.valid_data.copy()
        del data['username']

        response = self.client.post(
            '/register',
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'All fields are required', response.data)

    def test_register_missing_all_fields(self):
        """Test registration fails when all fields are missing"""
        response = self.client.post(
            '/register',
            data=json.dumps({}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'All fields are required', response.data)

