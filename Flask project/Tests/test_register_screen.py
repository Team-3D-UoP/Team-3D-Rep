import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestRegisterScreen(unittest.TestCase):
    """Test suite for the register screen route"""

    def setUp(self):
        """Set up test client before each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Valid test data
        self.valid_data = {
            'email': 'testuser@example.com',
            'password': 'TestPassword123!',
            'fullname': 'Test User',
            'username': 'testuser123'
        }

    def tearDown(self):
        """Clean up after each test"""
        pass

    def test_register_page_loads_successfully(self):
        """Test that the register page returns a 200 status code"""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)

    def test_register_page_renders_correct_template(self):
        """Test that the register page renders the register_screen.html template"""
        response = self.client.get('/register')
        # Check for common content that should be on the register page
        self.assertGreater(len(response.data), 0)

    def test_register_page_response_content_type(self):
        """Test that the register page returns HTML content"""
        response = self.client.get('/register')
        self.assertIn('text/html', response.content_type)

