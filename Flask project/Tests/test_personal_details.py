import os
import sys
import unittest

# Add the Flask project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestPersonalDetailsPage(unittest.TestCase):
    """Behavior-oriented tests for `personal_details.html`."""

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_personal_details_redirects_when_not_authenticated(self):
        """Unauthenticated users should be redirected to login."""
        response = self.client.get('/personal-details')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers.get('Location', ''))

    def test_personal_details_renders_when_authenticated(self):
        """Authenticated users should see the personal details page."""
        with self.client.session_transaction() as session:
            session['authenticated'] = True
            session['email'] = 'user@example.com'
            session['name'] = 'Test User'

        response = self.client.get('/personal-details')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Personal Details', response.data)
        self.assertIn(b'Edit Personal Details', response.data)
        self.assertIn(b'Save Changes', response.data)
        self.assertIn(b'Cancel', response.data)

    def test_personal_details_passes_session_values_into_template(self):
        """Username, email, and full name should be populated from session."""
        with self.client.session_transaction() as session:
            session['authenticated'] = True
            session['email'] = 'user@example.com'
            session['name'] = 'Test User'

        response = self.client.get('/personal-details')
        self.assertIn(b'value="Test User"', response.data)
        self.assertIn(b'value="user@example.com"', response.data)

    def test_personal_details_includes_navigation_links(self):
        """Sidebar and breadcrumb links should be present in the page."""
        with self.client.session_transaction() as session:
            session['authenticated'] = True
            session['email'] = 'user@example.com'
            session['name'] = 'Test User'

        response = self.client.get('/personal-details')
        self.assertIn(b'/account', response.data)
        self.assertIn(b'/my-orders', response.data)
        self.assertIn(b'/wishlist', response.data)
        self.assertIn(b'Account Overview', response.data)
        self.assertIn(b'My Orders', response.data)
        self.assertIn(b'My Wish List', response.data)
        self.assertIn(b'Personal Details', response.data)

    def test_personal_details_form_points_to_update_account(self):
        """The form should submit to the expected account update endpoint."""
        with self.client.session_transaction() as session:
            session['authenticated'] = True
            session['email'] = 'user@example.com'
            session['name'] = 'Test User'

        response = self.client.get('/personal-details')
        self.assertIn(b'method="POST" action="/update-account"', response.data)
        self.assertIn(b'name="username"', response.data)
        self.assertIn(b'name="email"', response.data)
        self.assertIn(b'name="full_name"', response.data)
        self.assertIn(b'name="password"', response.data)
        self.assertIn(b'name="confirm_password"', response.data)

    def test_personal_details_contains_responsive_layout_rules(self):
        """Responsive CSS rules should be present for mobile layouts."""
        with self.client.session_transaction() as session:
            session['authenticated'] = True
            session['email'] = 'user@example.com'
            session['name'] = 'Test User'

        response = self.client.get('/personal-details')
        self.assertIn(b'@media (max-width: 768px)', response.data)
        self.assertIn(b'.button-group {', response.data)
        self.assertIn(b'.container {', response.data)


if __name__ == '__main__':
    unittest.main()
