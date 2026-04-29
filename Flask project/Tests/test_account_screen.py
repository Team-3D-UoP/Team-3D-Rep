import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the Flask project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestAccountScreen(unittest.TestCase):
    """Test suite for the account screen template"""

    def setUp(self):
        """Set up test client before each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up after tests"""
        pass

    def test_account_screen_template_exists(self):
        """Test that the account screen file exists"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'account_screen.html')
        self.assertTrue(os.path.exists(template_path), "account_screen.html template file should exist")

    def test_account_screen_template_is_not_empty(self):
        """Test that the account screen has content"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'account_screen.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertGreater(len(content), 0, "account screen should not be empty")

    def test_account_screen_page_loads_successfully(self):
         """Test that the account screen page returns a 200 status code"""
         response = self.client.get('/account-screen')
         self.assertEqual(response.status_code, 200)

    def test_account_screen_page_renders_correct_template(self):
         """Test that the account screen page renders the account_screen.html template"""
         response = self.client.get('/account-screen')
         # Check for content that should be in account_screen.html
         self.assertIn(b'Account Screen', response.data)

    def test_account_screen_page_response_content_type(self):
         """Test that the account screen page returns HTML content"""
         response = self.client.get('/account-screen')
         self.assertIn('text/html', response.content_type)

    def test_account_screen_template_has_basic_html_structure(self):
        """Test that account_screen.html has basic HTML structure"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'account_screen.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('<!DOCTYPE html>', content, "Template should have DOCTYPE declaration")
        self.assertIn('<html', content, "Template should have html tag")
        self.assertIn('<head>', content, "Template should have head tag")
        self.assertIn('<body>', content, "Template should have body tag")

    def test_account_screen_template_has_title(self):
        """Test that account_screen.html has a title"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'account_screen.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('<title>', content, "Template should have a title tag")

    def test_account_screen_template_structure(self):
        """Test that account_screen.html follows expected structure"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'account_screen.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('<div', content, "Template should have div elements")
        self.assertIn('</html>', content, "Template should have closing html tag")


if __name__ == '__main__':
    unittest.main()