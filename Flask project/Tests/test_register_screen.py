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

        self.valid_data = {
            'email': 'testuser@example.com',
            'password': 'TestPassword123!',
            'fullname': 'Test User',
            'username': 'testuser123'
        }

    def tearDown(self):
        """Clean up after each test"""
        pass

