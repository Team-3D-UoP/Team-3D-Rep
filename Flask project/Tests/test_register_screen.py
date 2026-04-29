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

    def test_register_empty_email(self):
        """Test registration fails when email is empty"""
        data = self.valid_data.copy()
        data['email'] = ''

        response = self.client.post(
            '/register',
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'All fields are required', response.data)

    def test_register_empty_password(self):
        """Test registration fails when password is empty"""
        data = self.valid_data.copy()
        data['password'] = ''

        response = self.client.post(
            '/register',
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

    def test_register_empty_fullname(self):
        """Test registration fails when fullname is empty"""
        data = self.valid_data.copy()
        data['fullname'] = ''

        response = self.client.post(
            '/register',
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

    def test_register_empty_username(self):
        """Test registration fails when username is empty"""
        data = self.valid_data.copy()
        data['username'] = ''

        response = self.client.post(
            '/register',
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

    @patch('app.auth.create_user')
    def test_register_firebase_weak_password_error(self, mock_create_user):
        """Test registration fails with Firebase weak password error"""
        mock_create_user.side_effect = Exception('Password should be at least 6 characters')

        response = self.client.post(
            '/register',
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'error', response.data)

    @patch('app.auth.create_user')
    def test_register_firebase_email_already_exists(self, mock_create_user):
        """Test registration fails when email already exists"""
        mock_create_user.side_effect = Exception('Email already exists')

        response = self.client.post(
            '/register',
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Email already exists', response.data)

    @patch('app.auth.create_user')
    def test_register_firebase_invalid_email(self, mock_create_user):
        """Test registration fails with invalid email"""
        mock_create_user.side_effect = Exception('Invalid email address')

        response = self.client.post(
            '/register',
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

    @patch('app.auth.create_user')
    def test_register_firebase_uid_already_exists(self, mock_create_user):
        """Test registration fails when UID (username) already exists"""
        mock_create_user.side_effect = Exception('UID already exists')

        response = self.client.post(
            '/register',
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'UID already exists', response.data)

    @patch('app.auth.create_user')
    def test_register_generic_firebase_error(self, mock_create_user):
        """Test registration handles generic Firebase errors"""
        mock_create_user.side_effect = Exception('Firebase connection error')

        response = self.client.post(
            '/register',
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)

    def test_register_only_accepts_get_and_post(self):
        """Test that register route only accepts GET and POST methods"""
        # PUT should not be allowed
        response = self.client.put('/register')
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

        # DELETE should not be allowed
        response = self.client.delete('/register')
        self.assertEqual(response.status_code, 405)

    @patch('app.auth.create_user')
    def test_register_with_no_content_type(self, mock_create_user):
        """Test registration with form data and no explicit content type"""
        mock_create_user.return_value = MagicMock(uid='testuser123')

        response = self.client.post('/register', data=self.valid_data)
        self.assertEqual(response.status_code, 201)

    @patch('app.auth.create_user')
    def test_register_response_json_format(self, mock_create_user):
        """Test that successful registration returns properly formatted JSON"""
        mock_create_user.return_value = MagicMock(uid='testuser123')

        response = self.client.post(
            '/register',
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )

        response_data = json.loads(response.data)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['message'], 'Registration successful')

    @patch('app.auth.create_user')
    def test_register_error_response_json_format(self, mock_create_user):
        """Test that registration errors return properly formatted JSON"""
        mock_create_user.side_effect = Exception('Test error')

        response = self.client.post(
            '/register',
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )

        response_data = json.loads(response.data)
        self.assertIn('error', response_data)

    def test_register_with_special_characters_in_data(self):
        """Test registration with special characters in fields"""
        data = self.valid_data.copy()
        data['fullname'] = 'José María García-López'
        data['email'] = 'test+special@example.co.uk'

        with patch('app.auth.create_user') as mock_create_user:
            mock_create_user.return_value = MagicMock(uid='testuser123')

            response = self.client.post(
                '/register',
                data=json.dumps(data),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 201)

    def test_register_with_very_long_input(self):
        """Test registration with very long input strings"""
        data = self.valid_data.copy()
        data['fullname'] = 'A' * 500
        data['username'] = 'B' * 500

        with patch('app.auth.create_user') as mock_create_user:
            mock_create_user.return_value = MagicMock(uid='testuser123')

            response = self.client.post(
                '/register',
                data=json.dumps(data),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 201)

    def test_register_with_whitespace_only_fields(self):
        """Test registration fails with whitespace-only fields"""
        data = self.valid_data.copy()
        data['email'] = '   '

        response = self.client.post(
            '/register',
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

    @patch('app.auth.create_user')
    def test_register_duplicate_registration_attempt(self, mock_create_user):
        """Test that attempting to register twice with same email fails appropriately"""
        mock_create_user.return_value = MagicMock(uid='testuser123')
        response1 = self.client.post(
            '/register',
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, 201)

        # Second registration with same email fails
        mock_create_user.side_effect = Exception('Email already exists')
        response2 = self.client.post(
            '/register',
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 400)


if __name__ == '__main__':
    unittest.main()
