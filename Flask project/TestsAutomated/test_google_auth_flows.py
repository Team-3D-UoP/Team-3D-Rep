"""
Automated tests for Google Authentication workflows
Tests all partitions from the test plan:
- Successful Google login
- Non-registered Google account (first-time login)
- Invalid Google token
- Google OAuth callback
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import User


class TestGoogleAuthFlows(unittest.TestCase):
    """Test suite for Google authentication workflows based on test plan"""

    def setUp(self):
        """Set up test client and database before each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        # Mock Firebase as initialized for testing
        self.firebase_patcher = patch('app.firebase_initialized', True)
        self.mock_firebase_init = self.firebase_patcher.start()
        
        with self.app.app_context():
            db.create_all()
            # Create test user for Google login tests
            test_user = User(
                firebase_uid='google_user_12345',
                email='googleuser@gmail.com',
                username='googleuser',
                fullname='Google User'
            )
            db.session.add(test_user)
            db.session.commit()

    def tearDown(self):
        """Clean up after each test"""
        self.firebase_patcher.stop()
        
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # ========================
    # TEST PLAN PARTITION: Successful Google Login
    # ========================
    @patch('app.auth.verify_id_token')
    @patch('app.get_user_from_firebase')
    def test_google_login_successful(self, mock_get_user_firebase, mock_verify_token):
        """
        Partition: Successful Google login
        Input: Valid Google OAuth token from google.com
        Expected output: User is logged in and redirected to profile/dashboard
        Valid: ✓
        """
        # Mock Firebase to return valid Google user credentials
        mock_verify_token.return_value = {
            'uid': 'google_user_12345',
            'email': 'googleuser@gmail.com',
            'name': 'Google User',
            'iss': 'https://accounts.google.com'  # Google token issuer
        }
        
        mock_get_user_firebase.return_value = {
            'email': 'googleuser@gmail.com',
            'username': 'googleuser',
            'fullname': 'Google User'
        }
        
        test_data = {
            'token': 'valid_google_id_token',
            'user_data': {
                'email': 'googleuser@gmail.com',
                'username': 'googleuser'
            }
        }
        
        response = self.client.post(
            '/api/authenticate',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # Check response - successful authentication
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data.get('success'))

    # ========================
    # TEST PLAN PARTITION: Non-Registered Google Account
    # ========================
    @patch('app.auth.verify_id_token')
    @patch('app.save_user_to_firebase')
    def test_google_login_new_account(self, mock_firebase, mock_verify_token):
        """
        Partition: Non-registered Google account (first-time login)
        Input: Valid Google OAuth token but new account
        Expected output: New user account is created automatically
        Valid: ✓
        """
        # Mock Firebase to return new Google user (not registered yet)
        mock_verify_token.return_value = {
            'uid': 'google_new_user_54321',
            'email': 'newgoogleuser@gmail.com',
            'name': 'New Google User',
            'iss': 'https://accounts.google.com'
        }
        
        mock_firebase.return_value = True
        
        test_data = {
            'token': 'valid_google_id_token_new_user',
            'user_data': {
                'email': 'newgoogleuser@gmail.com',
                'username': 'newgoogleuser'
            }
        }
        
        response = self.client.post(
            '/api/authenticate',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # Should create new user and return success
        # Status could be 200 (user created) or 201 (created)
        self.assertIn(response.status_code, [200, 201])
        
        # Verify user was created in database
        with self.app.app_context():
            user = User.query.filter_by(
                firebase_uid='google_new_user_54321'
            ).first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'newgoogleuser@gmail.com')

    # ========================
    # TEST PLAN PARTITION: Invalid Google Token
    # ========================
    @patch('app.auth.verify_id_token')
    def test_google_login_invalid_token(self, mock_verify_token):
        """
        Partition: Invalid Google token
        Input: Expired or tampered Google OAuth token
        Expected output: Login fails with error message
        Valid: i (Invalid)
        """
        # Mock Firebase token verification to fail
        mock_verify_token.side_effect = Exception('Invalid token signature')
        
        test_data = {
            'token': 'invalid_or_expired_google_token',
            'user_data': {
                'email': 'user@gmail.com',
                'username': 'user'
            }
        }
        
        response = self.client.post(
            '/api/authenticate',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # Should fail authentication
        self.assertIn(response.status_code, [400, 401])

    # ========================
    # TEST PLAN PARTITION: Google OAuth Callback
    # ========================
    @patch('app.auth.verify_id_token')
    def test_google_oauth_callback(self, mock_verify_token):
        """
        Partition: Google OAuth callback/redirect
        Input: User redirected back from Google OAuth consent screen with valid token
        Expected output: User is authenticated and session is created
        Valid: ✓
        """
        mock_verify_token.return_value = {
            'uid': 'google_user_12345',
            'email': 'googleuser@gmail.com',
            'name': 'Google User',
            'iss': 'https://accounts.google.com'
        }
        
        test_data = {
            'token': 'google_callback_token',
            'user_data': {
                'email': 'googleuser@gmail.com',
                'username': 'googleuser'
            }
        }
        
        with self.client:
            response = self.client.post(
                '/api/authenticate',
                data=json.dumps(test_data),
                content_type='application/json'
            )
            
            # Callback should result in successful authentication
            self.assertEqual(response.status_code, 200)

    # ========================
    # ADDITIONAL: Google token with profile info
    # ========================
    @patch('app.auth.verify_id_token')
    def test_google_login_with_profile_data(self, mock_verify_token):
        """Test Google login extracts profile information correctly"""
        mock_verify_token.return_value = {
            'uid': 'google_profile_test',
            'email': 'profile.test@gmail.com',
            'name': 'Profile Test User',
            'picture': 'https://lh3.googleusercontent.com/a-/example',
            'email_verified': True,
            'iss': 'https://accounts.google.com'
        }
        
        test_data = {
            'token': 'google_profile_token',
            'user_data': {
                'email': 'profile.test@gmail.com',
                'username': 'profiletest'
            }
        }
        
        response = self.client.post(
            '/api/authenticate',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # Should handle profile data without errors
        self.assertIn(response.status_code, [200, 201])

    # ========================
    # ADDITIONAL: Google login with email mismatch
    # ========================
    @patch('app.auth.verify_id_token')
    def test_google_login_email_mismatch(self, mock_verify_token):
        """Test handling of email mismatch between Google token and request"""
        mock_verify_token.return_value = {
            'uid': 'google_mismatch_user',
            'email': 'verified@gmail.com',
            'name': 'Mismatch User',
            'iss': 'https://accounts.google.com'
        }
        
        # Email in request differs from token
        test_data = {
            'token': 'google_token_verified_at_gmail',
            'user_data': {
                'email': 'different@gmail.com',  # Mismatch!
                'username': 'mismatchuser'
            }
        }
        
        response = self.client.post(
            '/api/authenticate',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # App should handle this gracefully
        # Either use verified email from token or reject
        self.assertIn(response.status_code, [200, 400, 401])

    # ========================
    # ADDITIONAL: Multiple Google logins same account
    # ========================
    @patch('app.auth.verify_id_token')
    def test_google_login_repeated_account(self, mock_verify_token):
        """Test repeated Google login with same account (session persistence)"""
        mock_verify_token.return_value = {
            'uid': 'google_user_12345',
            'email': 'googleuser@gmail.com',
            'name': 'Google User',
            'iss': 'https://accounts.google.com'
        }
        
        test_data = {
            'token': 'google_repeat_token',
            'user_data': {
                'email': 'googleuser@gmail.com',
                'username': 'googleuser'
            }
        }
        
        # First login
        response1 = self.client.post(
            '/api/authenticate',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # Second login (immediate)
        response2 = self.client.post(
            '/api/authenticate',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # Both should succeed
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)


if __name__ == '__main__':
    unittest.main()
