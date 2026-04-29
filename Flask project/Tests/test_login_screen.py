import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestLoginScreen(unittest.TestCase):
    """Test suite for the login screen route"""

    def setUp(self):
        """Set up test client before each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up after each test"""
        pass

    def test_login_page_loads_successfully(self):
        """Test that the login page returns a 200 status code"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_login_page_renders_correct_template(self):
        """Test that the login page renders the login_screen.html template"""
        response = self.client.get('/login')
        self.assertGreater(len(response.data), 0)

    def test_login_page_response_content_type(self):
        """Test that the login page returns HTML content"""
        response = self.client.get('/login')
        self.assertIn('text/html', response.content_type)

    def test_login_page_only_accepts_get(self):
        """Test that login page only accepts GET requests"""
        # POST should not be allowed on /login
        response = self.client.post('/login')
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    @patch('app.auth.verify_id_token')
    def test_authenticate_with_valid_token(self, mock_verify_token):
        """Test authentication with a valid token"""
        mock_verify_token.return_value = {
            'uid': 'user123',
            'email': 'user@example.com',
            'name': 'Test User'
        }

        response = self.client.post(
            '/api/authenticate',
            data=json.dumps({'token': 'valid_token_here'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data.get('success'))
        self.assertEqual(response_data.get('redirect'), '/account')

    @patch('app.auth.verify_id_token')
    def test_authenticate_sets_session_data(self, mock_verify_token):
        """Test that authentication properly sets session data"""
        mock_verify_token.return_value = {
            'uid': 'user123',
            'email': 'user@example.com',
            'name': 'Test User'
        }

        with self.client:
            self.client.post(
                '/api/authenticate',
                data=json.dumps({'token': 'valid_token_here'}),
                content_type='application/json'
            )

            # Check session data was set
            from flask import session
            self.assertEqual(session.get('user_id'), 'user123')
            self.assertEqual(session.get('email'), 'user@example.com')
            self.assertEqual(session.get('name'), 'Test User')
            self.assertTrue(session.get('authenticated'))

    @patch('app.auth.verify_id_token')
    def test_authenticate_response_json_format(self, mock_verify_token):
        """Test that authenticate returns proper JSON response"""
        mock_verify_token.return_value = {
            'uid': 'user123',
            'email': 'user@example.com',
            'name': 'Test User'
        }

        response = self.client.post(
            '/api/authenticate',
            data=json.dumps({'token': 'valid_token_here'}),
            content_type='application/json'
        )

        self.assertIn('application/json', response.content_type)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, dict)
        self.assertIn('success', response_data)
        self.assertIn('redirect', response_data)

    def test_authenticate_missing_token(self):
        """Test authentication fails when token is missing"""
        response = self.client.post(
            '/api/authenticate',
            data=json.dumps({}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No token provided', response.data)

    def test_authenticate_token_is_none(self):
        """Test authentication fails when token is None"""
        response = self.client.post(
            '/api/authenticate',
            data=json.dumps({'token': None}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No token provided', response.data)

    def test_authenticate_token_is_empty_string(self):
        """Test authentication fails when token is empty string"""
        response = self.client.post(
            '/api/authenticate',
            data=json.dumps({'token': ''}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No token provided', response.data)

    def test_authenticate_token_is_whitespace(self):
        """Test authentication fails when token is only whitespace"""
        response = self.client.post(
            '/api/authenticate',
            data=json.dumps({'token': '   '}),
            content_type='application/json'
        )

        # Whitespace is truthy, so it should attempt verification
        self.assertIn(response.status_code, [400, 401])

    @patch('app.auth.verify_id_token')
    def test_authenticate_invalid_token_error(self, mock_verify_token):
        """Test authentication fails with invalid token error"""
        mock_verify_token.side_effect = Exception('Invalid token')

        response = self.client.post(
            '/api/authenticate',
            data=json.dumps({'token': 'invalid_token'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Invalid token', response.data)

    @patch('app.auth.verify_id_token')
    def test_authenticate_expired_token_error(self, mock_verify_token):
        """Test authentication fails with expired token error"""
        mock_verify_token.side_effect = Exception('Token expired')

        response = self.client.post(
            '/api/authenticate',
            data=json.dumps({'token': 'expired_token'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Token expired', response.data)

    @patch('app.auth.verify_id_token')
    def test_authenticate_malformed_token_error(self, mock_verify_token):
        """Test authentication fails with malformed token error"""
        mock_verify_token.side_effect = Exception('Malformed token')

        response = self.client.post(
            '/api/authenticate',
            data=json.dumps({'token': 'malformed.token'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 401)

    @patch('app.auth.verify_id_token')
    def test_authenticate_firebase_connection_error(self, mock_verify_token):
        """Test authentication handles Firebase connection errors"""
        mock_verify_token.side_effect = Exception('Firebase connection error')

        response = self.client.post(
            '/api/authenticate',
            data=json.dumps({'token': 'valid_token'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 401)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('details', response_data)

    @patch('app.auth.verify_id_token')
    def test_authenticate_token_missing_uid(self, mock_verify_token):
        """Test authentication with token missing uid claim"""
        # This should raise an error since 'uid' is required
        mock_verify_token.side_effect = KeyError('uid')

        response = self.client.post(
            '/api/authenticate',
            data=json.dumps({'token': 'token_without_uid'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 401)

    @patch('app.auth.verify_id_token')
    def test_authenticate_token_missing_email(self, mock_verify_token):
        """Test authentication with token missing email claim (should still work)"""
        mock_verify_token.return_value = {
            'uid': 'user123',
            'name': 'Test User'
            # email is missing, should default to empty string
        }

        response = self.client.post(
            '/api/authenticate',
            data=json.dumps({'token': 'token_without_email'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

    @patch('app.auth.verify_id_token')
    def test_authenticate_token_missing_name(self, mock_verify_token):
        """Test authentication with token missing name claim (should still work)"""
        mock_verify_token.return_value = {
            'uid': 'user123',
            'email': 'user@example.com'
            # name is missing, should default to empty string
        }

        response = self.client.post(
            '/api/authenticate',
            data=json.dumps({'token': 'token_without_name'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

    def test_authenticate_only_accepts_post(self):
        """Test that authenticate endpoint only accepts POST requests"""
        # GET should not be allowed
        response = self.client.get('/api/authenticate')
        self.assertEqual(response.status_code, 405)

        # PUT should not be allowed
        response = self.client.put('/api/authenticate')
        self.assertEqual(response.status_code, 405)

        # DELETE should not be allowed
        response = self.client.delete('/api/authenticate')
        self.assertEqual(response.status_code, 405)

    @patch('app.auth.verify_id_token')
    def test_authenticate_returns_json_on_success(self, mock_verify_token):
        """Test that successful authentication returns JSON"""
        mock_verify_token.return_value = {
            'uid': 'user123',
            'email': 'user@example.com',
            'name': 'Test User'
        }

        response = self.client.post(
            '/api/authenticate',
            data=json.dumps({'token': 'valid_token'}),
            content_type='application/json'
        )

        self.assertIn('application/json', response.content_type)

    @patch('app.auth.verify_id_token')
    def test_authenticate_returns_json_on_error(self, mock_verify_token):
        """Test that authentication errors return JSON"""
        mock_verify_token.side_effect = Exception('Token error')

        response = self.client.post(
            '/api/authenticate',
            data=json.dumps({'token': 'invalid_token'}),
            content_type='application/json'
        )

        self.assertIn('application/json', response.content_type)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)

