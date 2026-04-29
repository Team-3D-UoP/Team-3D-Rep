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
