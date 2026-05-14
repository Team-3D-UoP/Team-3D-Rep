import unittest
import sys
import os
from pathlib import Path

# Add parent directory to path to import app and models
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask
from app import app, db
from models import User, SellerReview
import json
from unittest.mock import patch, MagicMock


class TestSellerDetailsFlows(unittest.TestCase):
    """Test suite for seller details and profile functionality"""

    def setUp(self):
        """Set up test client and database before each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            # Create test user
            test_user = User(
                firebase_uid='test_firebase_uid',
                username='testuser',
                email='test@example.com',
                fullname='Test User'
            )
            db.session.add(test_user)
            db.session.commit()

    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_seller_details_valid_id(self):
        """Test retrieving seller details for a valid seller ID"""
        with self.client:
            response = self.client.get('/seller/1')
            # Accept 200 (success), 404 (seller not found), or 302 (redirect to login)
            self.assertIn(response.status_code, [200, 302, 404])
            # Should not return server error
            self.assertNotEqual(response.status_code, 500)
            # Response data should not be empty
            self.assertIsNotNone(response.data)

    def test_get_seller_details_invalid_id(self):
        """Test retrieving seller details for an invalid seller ID"""
        with self.client:
            # Test with a very large non-existent seller ID
            response = self.client.get('/seller/999999')
            # Should handle gracefully - either 404 or 200
            self.assertIn(response.status_code, [200, 302, 404])
            # Should not crash with 500 error
            self.assertNotEqual(response.status_code, 500)

    def test_get_seller_details_negative_id(self):
        """Test retrieving seller details with negative seller ID"""
        with self.client:
            # Test with negative ID as edge case
            response = self.client.get('/seller/-1')
            # Should handle gracefully
            self.assertIn(response.status_code, [200, 302, 404])
            # Should not return server error
            self.assertNotEqual(response.status_code, 500)


if __name__ == '__main__':
    unittest.main()
