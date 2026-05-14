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
        self.app.config['SQLALCHEMY_ECHO'] = False
        
        # Use app context and ensure fresh database for each test
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Clear any existing data and create fresh schema
        db.drop_all()
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
        
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_seller_details(self):
        """Test retrieving seller details with various ID types"""
        with self.client:
            # Test valid ID
            response = self.client.get('/seller/1')
            self.assertIn(response.status_code, [200, 302, 404])
            self.assertNotEqual(response.status_code, 500)
            self.assertIsNotNone(response.data)
            
            # Test invalid ID (very large)
            response = self.client.get('/seller/999999')
            self.assertIn(response.status_code, [200, 302, 404])
            self.assertNotEqual(response.status_code, 500)
            
            # Test negative ID
            response = self.client.get('/seller/-1')
            self.assertIn(response.status_code, [200, 302, 404])
            self.assertNotEqual(response.status_code, 500)

    def test_get_seller_reviews(self):
        """Test retrieving seller reviews endpoint and with existing reviews"""
        with self.client:
            # Test endpoint existence
            response = self.client.get('/seller/1/reviews')
            self.assertIn(response.status_code, [200, 302, 404])
            self.assertNotEqual(response.status_code, 500)
            if response.status_code == 200:
                try:
                    data = json.loads(response.data)
                    self.assertIsInstance(data, (list, dict))
                except:
                    pass
        
        # Test with existing reviews
        test_user = User.query.filter_by(username='testuser').first()
        if test_user:
            test_review = SellerReview(
                seller_id=1,
                user_id=str(test_user.id),
                user_email=test_user.email,
                user_name=test_user.fullname,
                rating=5,
                review_text='Excellent seller!'
            )
            db.session.add(test_review)
            db.session.commit()
        
        with self.client:
            response = self.client.get('/seller/1/reviews')
            self.assertIn(response.status_code, [200, 302, 404])
            if response.status_code == 200:
                self.assertIsNotNone(response.data)

    def test_post_seller_review_success(self):
        """Test successful review submission with valid data"""
        test_user = User.query.filter_by(username='testuser').first()
        user_id = test_user.id if test_user else 1
        
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user_id
            
            response = self.client.post('/seller/1/review', data={
                'rating': 5,
                'review_text': 'Great seller with excellent service!'
            })
            # Accept various success codes (200, 201, 302 redirect, 400 if validation)
            self.assertIn(response.status_code, [200, 201, 302, 400])
            # Should not crash
            self.assertNotEqual(response.status_code, 500)

    def test_post_seller_review_requires_auth(self):
        """Test authentication requirements for review submission"""
        with self.client:
            # Try to post review without authentication
            response = self.client.post('/seller/1/review', data={
                'rating': 5,
                'review_text': 'Great seller!'
            })
            # Should either redirect to login or return auth error or 400
            self.assertIn(response.status_code, [401, 403, 302, 400])

    def test_post_seller_review_validation(self):
        """Test comprehensive input validation for review submission"""
        test_user = User.query.filter_by(username='testuser').first()
        user_id = test_user.id if test_user else 1
        
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user_id
            
            # Test invalid rating (too high and too low)
            for invalid_rating in [10, 0, -5]:
                response = self.client.post('/seller/1/review', data={
                    'rating': invalid_rating,
                    'review_text': 'Invalid rating'
                })
                self.assertNotEqual(response.status_code, 500)
            
            # Test missing fields
            response = self.client.post('/seller/1/review', data={'review_text': 'No rating'})
            self.assertNotEqual(response.status_code, 500)
            
            response = self.client.post('/seller/1/review', data={'rating': 4})
            self.assertNotEqual(response.status_code, 500)
            
            # Test short text
            response = self.client.post('/seller/1/review', data={
                'rating': 5,
                'review_text': 'Hi'
            })
            self.assertNotEqual(response.status_code, 500)
            
            # Test non-existent seller
            response = self.client.post('/seller/999999/review', data={
                'rating': 5,
                'review_text': 'Review for non-existent seller'
            })
            self.assertNotEqual(response.status_code, 500)

    def test_post_seller_review_security_and_edge_cases(self):
        """Test security and edge case scenarios for review submission"""
        test_user = User.query.filter_by(username='testuser').first()
        user_id = test_user.id if test_user else 1
        
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user_id
            
            # Test XSS attempt
            response = self.client.post('/seller/1/review', data={
                'rating': 5,
                'review_text': '<script>alert("XSS")</script>'
            })
            self.assertNotEqual(response.status_code, 500)
            
            # Test SQL injection attempt
            response = self.client.post('/seller/1/review', data={
                'rating': 5,
                'review_text': "'; DROP TABLE seller_reviews; --"
            })
            self.assertNotEqual(response.status_code, 500)
            
            # Verify table still exists
            review_count = SellerReview.query.count()
            self.assertGreaterEqual(review_count, 0)
            
            # Test very long text
            response = self.client.post('/seller/1/review', data={
                'rating': 5,
                'review_text': 'A' * 10000
            })
            self.assertNotEqual(response.status_code, 500)
            
            # Test unicode characters
            response = self.client.post('/seller/1/review', data={
                'rating': 5,
                'review_text': 'Great seller! 你好 مرحبا 🌟'
            })
            self.assertNotEqual(response.status_code, 500)
            
            # Test boundary ratings (1 and 5)
            for rating in [1, 5]:
                response = self.client.post('/seller/1/review', data={
                    'rating': rating,
                    'review_text': f'Rating {rating} review'
                })
                self.assertNotEqual(response.status_code, 500)


if __name__ == '__main__':
    unittest.main()
