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


    def test_dashboard_users_requires_authentication(self):
        """Dashboard users endpoint rejects unauthenticated requests"""
        response = self.client.get('/api/dashboard/users')
        payload = response.get_json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(payload.get('error'), 'Unauthorized')

    def test_dashboard_reviews_requires_authentication(self):
        """Dashboard reviews endpoint rejects unauthenticated requests"""
        response = self.client.get('/api/dashboard/reviews')
        payload = response.get_json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(payload.get('error'), 'Unauthorized')

    def test_dashboard_carts_requires_authentication(self):
        """Dashboard carts endpoint rejects unauthenticated requests"""
        response = self.client.get('/api/dashboard/carts')
        payload = response.get_json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(payload.get('error'), 'Unauthorized')



    def test_dashboard_users_returns_data_when_authenticated(self):
        """Authenticated admin can access users dashboard"""
        self.client.post(
            '/api/admin/login',
            json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD}
        )
        
        response = self.client.get('/api/dashboard/users')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('count', payload)
        self.assertIn('users', payload)
        self.assertIsInstance(payload.get('users'), list)

    def test_dashboard_reviews_returns_data_when_authenticated(self):
        """Authenticated admin can access reviews dashboard"""
        self.client.post(
            '/api/admin/login',
            json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD}
        )
        
        response = self.client.get('/api/dashboard/reviews')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('count', payload)
        self.assertIn('reviews', payload)
        self.assertIsInstance(payload.get('reviews'), list)

    def test_dashboard_carts_returns_data_when_authenticated(self):
        """Authenticated admin can access carts dashboard"""
        self.client.post(
            '/api/admin/login',
            json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD}
        )
        
        response = self.client.get('/api/dashboard/carts')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('count', payload)
        self.assertIn('cart_count', payload)



    def test_admin_logout_clears_session(self):
        """Admin logout clears session and requires re-authentication"""
        self.client.post(
            '/api/admin/login',
            json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD}
        )
        
        response_before = self.client.get('/api/dashboard/users')
        self.assertEqual(response_before.status_code, 200)
        
        logout_response = self.client.post('/api/admin/logout')
        logout_payload = logout_response.get_json()
        self.assertEqual(logout_response.status_code, 200)
        self.assertTrue(logout_payload.get('success'))
        
        response_after = self.client.get('/api/dashboard/users')
        self.assertEqual(response_after.status_code, 401)


if __name__ == '__main__':
    unittest.main()
