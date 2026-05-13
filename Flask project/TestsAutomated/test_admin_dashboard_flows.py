"""
Automated tests for Admin Dashboard flows
This file will cover admin login plus admin dashboard API behavior
from the test plan.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, ADMIN_EMAIL, ADMIN_PASSWORD


class TestAdminDashboardFlows(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()


    def test_admin_login_with_correct_email_and_password(self):
        """Admin can login with correct email and password"""
        response = self.client.post(
            '/api/admin/login',
            json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD}
        )
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload.get('success'))
        self.assertEqual(payload.get('message'), 'Admin login successful')

    def test_admin_login_with_wrong_email(self):
        """Admin login fails with incorrect email"""
        response = self.client.post(
            '/api/admin/login',
            json={'email': 'wrong@example.com', 'password': ADMIN_PASSWORD}
        )
        payload = response.get_json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(payload.get('error'), 'Invalid admin credentials')

    def test_admin_login_with_wrong_password(self):
        """Admin login fails with incorrect password"""
        response = self.client.post(
            '/api/admin/login',
            json={'email': ADMIN_EMAIL, 'password': 'wrongpassword'}
        )
        payload = response.get_json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(payload.get('error'), 'Invalid admin credentials')


if __name__ == '__main__':
    unittest.main()
