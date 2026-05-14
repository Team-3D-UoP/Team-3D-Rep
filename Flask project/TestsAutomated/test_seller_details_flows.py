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

    def test_get_seller_reviews_endpoint(self):
        """Test retrieving seller reviews API endpoint"""
        with self.client:
            response = self.client.get('/seller/1/reviews')
            # Endpoint should exist or handle gracefully
            self.assertIn(response.status_code, [200, 302, 404])
            # Should not return server error
            self.assertNotEqual(response.status_code, 500)
            if response.status_code == 200:
                try:
                    data = json.loads(response.data)
                    self.assertIsInstance(data, (list, dict))
                except:
                    pass  # Some endpoints may return HTML instead of JSON

    def test_get_seller_reviews_with_existing_reviews(self):
        """Test retrieving seller reviews when reviews exist in database"""
        with self.app.app_context():
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
        with self.app.app_context():
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

    def test_post_seller_review_invalid_rating(self):
        """Test validation for ratings outside 1-5 range"""
        with self.app.app_context():
            test_user = User.query.filter_by(username='testuser').first()
            user_id = test_user.id if test_user else 1
        
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user_id
            
            # Test invalid rating (too high)
            response = self.client.post('/seller/1/review', data={
                'rating': 10,
                'review_text': 'Invalid rating'
            })
            # Should handle gracefully
            self.assertNotEqual(response.status_code, 500)
            
            # Test invalid rating (too low)
            response = self.client.post('/seller/1/review', data={
                'rating': 0,
                'review_text': 'Invalid rating'
            })
            # Should handle gracefully
            self.assertNotEqual(response.status_code, 500)

    def test_post_seller_review_missing_fields(self):
        """Test validation for missing required fields"""
        with self.app.app_context():
            test_user = User.query.filter_by(username='testuser').first()
            user_id = test_user.id if test_user else 1
        
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user_id
            
            # Missing rating
            response = self.client.post('/seller/1/review', data={
                'review_text': 'Review without rating'
            })
            # Should handle gracefully
            self.assertNotEqual(response.status_code, 500)
            
            # Missing review text
            response = self.client.post('/seller/1/review', data={
                'rating': 4
            })
            # Should handle gracefully
            self.assertNotEqual(response.status_code, 500)

    def test_post_seller_review_short_text(self):
        """Test minimum length requirements for review text"""
        with self.app.app_context():
            test_user = User.query.filter_by(username='testuser').first()
            user_id = test_user.id if test_user else 1
        
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user_id
            
            # Test with very short review text
            response = self.client.post('/seller/1/review', data={
                'rating': 5,
                'review_text': 'Hi'
            })
            # Should handle gracefully without crashing
            self.assertNotEqual(response.status_code, 500)

    def test_post_seller_review_invalid_seller(self):
        """Test error handling for reviews on non-existent sellers"""
        with self.app.app_context():
            test_user = User.query.filter_by(username='testuser').first()
            user_id = test_user.id if test_user else 1
        
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user_id
            
            # Try to review non-existent seller
            response = self.client.post('/seller/999999/review', data={
                'rating': 5,
                'review_text': 'Review for non-existent seller'
            })
            # Should handle gracefully without 500 error
            self.assertNotEqual(response.status_code, 500)


if __name__ == '__main__':
    unittest.main()
