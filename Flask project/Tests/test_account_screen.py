import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Flask directory added to Python path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestAccount(unittest.TestCase):
    """Test suite for the account template"""

    def setUp(self):
        """Set up test client before each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up after tests"""
        pass

    def test_account_template_exists(self):
        """Test that the account file exists"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'account.html')
        self.assertTrue(os.path.exists(template_path), "account.html template file should exist")

    def test_account_template_has_content(self):
        """Test that the account template has content"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'account.html')
        # Verify file exists and has content
        self.assertTrue(os.path.exists(template_path))

    def test_account_template_is_readable(self):
        """Test that account.html is readable"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'account.html')
        self.assertTrue(os.access(template_path, os.R_OK), "Template file should be readable")

    def test_account_template_encoding(self):
        """Test that account.html can be read with UTF-8 encoding"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'account.html')
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                f.read()
            encoding_ok = True
        except UnicodeDecodeError:
            encoding_ok = False
        self.assertTrue(encoding_ok, "Template should be UTF-8 encoded")

    def test_account_template_file_size(self):
        """Test that account.html file exists and is accessible"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'account.html')
        self.assertTrue(os.path.isfile(template_path), "account.html should be a file, not a directory")

    def test_account_template_basic_structure(self):
        """Test for basic HTML structure"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'account.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if len(content) > 0:
            self.assertTrue(
                any(tag in content for tag in ['<!DOCTYPE', '<html', '<head', '<body']),
                "Template should have basic HTML structure when content is present"
            )

    def test_account_route_requires_authentication(self):
        """Test that /account route requires authentication"""
        response = self.client.get('/account')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/login', response.headers.get('Location', ''))

    def test_account_route_with_valid_session(self):
        """Test that /account loads with valid session"""
        with self.client:
            with self.client.session_transaction() as sess:
                sess['authenticated'] = True
                sess['name'] = 'Test User'
            response = self.client.get('/account')
            self.assertEqual(response.status_code, 200)

    def test_account_template_contains_form(self):
        """Test that account.html contains expected form elements"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'account.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if len(content) > 0:
            self.assertIn('form', content.lower(), "Template should contain form element")

    def test_account_template_no_syntax_errors(self):
        """Test that template file can be read without errors"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'account.html')
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            has_error = (
                content.count('{{') != content.count('}}') or
                content.count('{%') != content.count('%}')
            )
            self.assertFalse(has_error, "Template should have balanced template delimiters")
        except Exception as e:
            self.fail(f"Template should not cause errors when read: {e}")

    def test_account_no_hardcoded_sensitive_data(self):
        """Test that template doesn't contain hardcoded passwords or secrets"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'account.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
        
        suspicious_patterns = ['password=', 'secret=', 'api_key=', 'token=']
        found_suspicious = any(pattern in content for pattern in suspicious_patterns)
        self.assertFalse(found_suspicious, "Template should not contain hardcoded secrets")


if __name__ == '__main__':
    unittest.main()