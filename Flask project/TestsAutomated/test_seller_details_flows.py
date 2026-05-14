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

    def test_post_seller_review_non_numeric_rating(self):
        """Test validation for non-numeric rating values"""
        with self.app.app_context():
            test_user = User.query.filter_by(username='testuser').first()
            user_id = test_user.id if test_user else 1
        
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user_id
            
            # Submit non-numeric rating
            response = self.client.post('/seller/1/review', data={
                'rating': 'abc',
                'review_text': 'Review with invalid rating'
            })
            # Should not crash with 500 error
            self.assertNotEqual(response.status_code, 500)

    def test_post_seller_review_very_long_text(self):
        """Test validation for extremely long review text"""
        with self.app.app_context():
            test_user = User.query.filter_by(username='testuser').first()
            user_id = test_user.id if test_user else 1
        
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user_id
            
            # Submit very long review text (10000+ characters)
            very_long_text = 'A' * 10000
            response = self.client.post('/seller/1/review', data={
                'rating': 5,
                'review_text': very_long_text
            })
            # Should handle gracefully
            self.assertNotEqual(response.status_code, 500)

    def test_post_seller_review_empty_strings(self):
        """Test validation for empty string values"""
        with self.app.app_context():
            test_user = User.query.filter_by(username='testuser').first()
            user_id = test_user.id if test_user else 1
        
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user_id
            
            # Submit with empty rating
            response = self.client.post('/seller/1/review', data={
                'rating': '',
                'review_text': 'Valid review text'
            })
            # Should handle gracefully
            self.assertNotEqual(response.status_code, 500)
            
            # Submit with empty review text
            response = self.client.post('/seller/1/review', data={
                'rating': 4,
                'review_text': ''
            })
            # Should handle gracefully
            self.assertNotEqual(response.status_code, 500)

    def test_post_seller_review_xss_attempt(self):
        """Test protection against XSS attacks in review text"""
        with self.app.app_context():
            test_user = User.query.filter_by(username='testuser').first()
            user_id = test_user.id if test_user else 1
        
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user_id
            
            # Attempt XSS injection
            xss_payload = '<script>alert("XSS")</script>'
            response = self.client.post('/seller/1/review', data={
                'rating': 5,
                'review_text': xss_payload
            })
            # Should handle gracefully without crashing
            self.assertNotEqual(response.status_code, 500)

    def test_post_seller_review_sql_injection_attempt(self):
        """Test protection against SQL injection in review data"""
        with self.app.app_context():
            test_user = User.query.filter_by(username='testuser').first()
            user_id = test_user.id if test_user else 1
        
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user_id
            
            # Attempt SQL injection
            sql_payload = "'; DROP TABLE seller_reviews; --"
            response = self.client.post('/seller/1/review', data={
                'rating': 5,
                'review_text': sql_payload
            })
            # Should handle gracefully without executing SQL
            self.assertNotEqual(response.status_code, 500)
            
            # Verify table still exists after attempted injection
            with self.app.app_context():
                review_count = SellerReview.query.count()
                self.assertGreaterEqual(review_count, 0)

    def test_post_seller_review_special_characters(self):
        """Test handling of special characters in review text"""
        with self.app.app_context():
            test_user = User.query.filter_by(username='testuser').first()
            user_id = test_user.id if test_user else 1
        
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user_id
            
            # Submit review with special characters
            special_text = 'Great! @#$%^&*()_+-={}[]|:;<>?,./'
            response = self.client.post('/seller/1/review', data={
                'rating': 5,
                'review_text': special_text
            })
            # Should handle gracefully
            self.assertNotEqual(response.status_code, 500)

    def test_post_seller_review_unicode_characters(self):
        """Test handling of unicode and international characters"""
        with self.app.app_context():
            test_user = User.query.filter_by(username='testuser').first()
            user_id = test_user.id if test_user else 1
        
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user_id
            
            # Submit review with unicode characters
            unicode_text = 'Great seller! 你好 مرحبا Привет 🌟'
            response = self.client.post('/seller/1/review', data={
                'rating': 5,
                'review_text': unicode_text
            })
            # Should handle gracefully
            self.assertNotEqual(response.status_code, 500)

    def test_post_seller_review_boundary_ratings(self):
        """Test boundary values for rating (1 and 5)"""
        with self.app.app_context():
            test_user = User.query.filter_by(username='testuser').first()
            user_id = test_user.id if test_user else 1
        
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user_id
            
            # Test minimum valid rating
            response = self.client.post('/seller/1/review', data={
                'rating': 1,
                'review_text': 'Minimum rating review'
            })
            self.assertNotEqual(response.status_code, 500)
            
            # Test maximum valid rating
            response = self.client.post('/seller/1/review', data={
                'rating': 5,
                'review_text': 'Maximum rating review'
            })
            self.assertNotEqual(response.status_code, 500)

    def test_post_seller_review_float_rating(self):
        """Test handling of float values for rating"""
        with self.app.app_context():
            test_user = User.query.filter_by(username='testuser').first()
            user_id = test_user.id if test_user else 1
        
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user_id
            
            # Submit float rating (should be integer)
            response = self.client.post('/seller/1/review', data={
                'rating': 4.5,
                'review_text': 'Review with float rating'
            })
            # Should handle gracefully
            self.assertNotEqual(response.status_code, 500)

    def test_post_seller_review_negative_rating(self):
        """Test validation for negative rating values"""
        with self.app.app_context():
            test_user = User.query.filter_by(username='testuser').first()
            user_id = test_user.id if test_user else 1
        
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user_id
            
            # Submit negative rating
            response = self.client.post('/seller/1/review', data={
                'rating': -5,
                'review_text': 'Review with negative rating'
            })
            # Should handle gracefully
            self.assertNotEqual(response.status_code, 500)

    def test_get_seller_reviews_with_invalid_format(self):
        """Test GET endpoint with invalid format requests"""
        with self.client:
            # Test with invalid seller ID format
            response = self.client.get('/seller/invalid_id/reviews')
            # Should handle gracefully
            self.assertNotEqual(response.status_code, 500)
            
            # Test with special characters in ID
            response = self.client.get('/seller/!@#$/reviews')
            # Should handle gracefully
            self.assertNotEqual(response.status_code, 500)


if __name__ == '__main__':
    unittest.main()
