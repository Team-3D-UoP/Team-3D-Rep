"""
Automated tests for Admin Login flows
This file will cover admin authentication API behavior
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, ADMIN_EMAIL, ADMIN_PASSWORD


class TestAdminLoginFlows(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_admin_login_success(self):
        """Admin login with correct credentials"""
        response = self.client.post(
            '/api/admin/login',
            json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD}
        )
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload.get('success'))
        self.assertEqual(payload.get('message'), 'Admin login successful')

    def test_admin_login_wrong_email(self):
        """Admin login fails with incorrect email"""
        response = self.client.post(
            '/api/admin/login',
            json={'email': 'wrong@example.com', 'password': ADMIN_PASSWORD}
        )
        payload = response.get_json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(payload.get('error'), 'Invalid admin credentials')

    def test_admin_login_wrong_password(self):
        """Admin login fails with incorrect password"""
        response = self.client.post(
            '/api/admin/login',
            json={'email': ADMIN_EMAIL, 'password': 'wrongpassword'}
        )
        payload = response.get_json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(payload.get('error'), 'Invalid admin credentials')

    def test_admin_login_missing_email(self):
        """Admin login fails with missing email"""
        response = self.client.post(
            '/api/admin/login',
            json={'password': ADMIN_PASSWORD}
        )
        payload = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', payload)

    def test_admin_login_missing_password(self):
        """Admin login fails with missing password"""
        response = self.client.post(
            '/api/admin/login',
            json={'email': ADMIN_EMAIL}
        )
        payload = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', payload)

    def test_admin_login_empty_request(self):
        """Admin login fails with empty request body"""
        response = self.client.post(
            '/api/admin/login',
            json={}
        )
        payload = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', payload)

    def test_admin_logout_success(self):
        """Admin logout clears session"""
        # First login
        self.client.post(
            '/api/admin/login',
            json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD}
        )

        # Then logout
        response = self.client.post('/api/admin/logout')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload.get('success'))
        self.assertEqual(payload.get('message'), 'Logged out')

    def test_admin_logout_without_login(self):
        """Admin logout works even without prior login"""
        response = self.client.post('/api/admin/logout')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload.get('success'))

    def test_protected_route_after_logout(self):
        """Accessing protected admin route fails after logout"""
        # Login first
        self.client.post(
            '/api/admin/login',
            json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD}
        )

        # Logout
        self.client.post('/api/admin/logout')

        # Try to access protected route
        response = self.client.get('/api/dashboard/users')
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()