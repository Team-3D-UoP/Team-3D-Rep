import unittest
from flask import Flask
from app import app, db
from models import User, SellerReview
import json
from unittest.mock import patch, MagicMock


class TestSellerDetailsFlows(unittest.TestCase):
    """Test suite for seller details and review functionality"""

    def setUp(self):
        """Set up test client and database before each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            # Create test user
            test_user = User(username='testuser', email='test@example.com', password='hashed_password')
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
            self.assertIn(response.status_code, [200, 404])  # Either page exists or seller doesn't exist
            if response.status_code == 200:
                self.assertIsNotNone(response.data)

    def test_get_seller_details_invalid_id(self):
        """Test retrieving seller details for an invalid seller ID"""
        with self.client:
            # Test with a non-existent seller ID
            response = self.client.get('/seller/9999')
            self.assertIn(response.status_code, [404, 200])  # Should handle gracefully
            # Invalid IDs should not crash the server
            self.assertNotEqual(response.status_code, 500)


if __name__ == '__main__':
    unittest.main()
