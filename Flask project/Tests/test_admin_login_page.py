import os
import sys
import unittest

# Ensure project root is on sys.path so imports like `from app import app` work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class AdminLoginPageTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_admin_login_page_renders(self):
        rv = self.client.get('/admin-login')
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode('utf-8')
        self.assertIn('Admin Portal', data)
        self.assertIn('Secure Admin Access', data)
        self.assertIn('Login to Admin Dashboard', data)

    def test_admin_login_page_contains_form_fields(self):
        rv = self.client.get('/admin-login')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('id="admin-login-form"', data)
            self.assertIn('input type="email"', data)
            self.assertIn('input type="password"', data)
            self.assertIn('id="email"', data)
            self.assertIn('id="password"', data)
            self.assertIn('required', data)

    def test_admin_login_page_contains_warning_and_back_link(self):
        rv = self.client.get('/admin-login')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('authorized administrators only', data)
            self.assertIn('Unauthorized access attempts are logged', data)
            self.assertIn('← Back to Home', data)
            self.assertIn('href="/"', data)

    def test_admin_login_page_contains_submit_handler(self):
        rv = self.client.get('/admin-login')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn("addEventListener('submit'", data)
            self.assertIn("fetch('/api/admin/login'", data)
            self.assertIn('method: \'POST\'', data)
            self.assertIn('Content-Type', data)
            self.assertIn('window.location.href = data.redirect || \'/admin\'', data)

    def test_admin_login_page_contains_error_handling(self):
        rv = self.client.get('/admin-login')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('error-message', data)
            self.assertIn('Admin login failed', data)
            self.assertIn('Login error: ', data)
            self.assertIn('errorMsg.style.display = \'block\'', data)

    def test_admin_login_page_contains_styling(self):
        rv = self.client.get('/admin-login')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('.login-container', data)
            self.assertIn('.login-header', data)
            self.assertIn('.warning-box', data)
            self.assertIn('@media (max-width: 480px)', data)
            self.assertIn('background-color: #c33', data)


if __name__ == '__main__':
    unittest.main()
