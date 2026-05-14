"""
Automated tests for User Reviews flows
Tests all partitions from the test plan:
- View no reviews message
- Audit review (valid submission)
- Submit review without rating
- Submit empty review
- View existing reviews
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import User, ProductReview, SellerReview


class TestUserReviewsFlows(unittest.TestCase):
    """Test suite for user reviews workflows based on test plan"""

    def setUp(self):
        """Set up test client and database before each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        # Mock Firebase as initialized for testing
        self.firebase_patcher = patch('app.firebase_initialized', True)
        self.mock_firebase_init = self.firebase_patcher.start()
        
        with self.app.app_context():
            db.create_all()
            # Create test user
            test_user = User(
                firebase_uid='review_test_user',
                email='reviewuser@gmail.com',
                username='reviewuser',
                fullname='Review Test User'
            )
            db.session.add(test_user)
            db.session.commit()
            self.test_user_id = test_user.id
            self.test_product_id = 1001  # Using product from OFFER_PRODUCTS (Pressure Washer)

    def tearDown(self):
        """Clean up after each test"""
        self.firebase_patcher.stop()
        
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # ========================
    # TEST PLAN PARTITION: View No Reviews Message
    # ========================
    def test_view_no_reviews_message(self):
        """
        Partition: View no reviews message
        Input: User opens a product page with no existing reviews
        Expected output: Message display saying "No user reviews yet. Be the first to review!"
        Valid: ✓
        """
        response = self.client.get(f'/product/{self.test_product_id}/reviews')
        
        # Should return 200 with empty reviews list
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data.get('success'))
        self.assertEqual(response_data.get('count'), 0)
        self.assertEqual(len(response_data.get('reviews', [])), 0)

    # ========================
    # TEST PLAN PARTITION: Audit Review (Valid Submission)
    # ========================
    @patch('app.save_review_to_firebase')
    def test_submit_valid_review(self, mock_firebase):
        """
        Partition: Audit review (valid submission)
        Input: User enters a star rating, enters "Good Product" comment, and clicks submit review
        Expected output: Review is submitted and appears in user profile
        Valid: ✓
        """
        mock_firebase.return_value = True
        
        # Set up session with user_id manually (Flask test client limitation)
        with self.client:
            # Make a dummy request to establish a session
            self.client.get('/')
            # Manually set session values
            from flask import session
            with self.client.session_transaction() as sess:
                sess['user_id'] = self.test_user_id
                sess['email'] = 'reviewuser@gmail.com'
                sess['name'] = 'Review Test User'
            
            # Submit valid review
            review_data = {
                'rating': 5,
                'review_text': 'Good Product'
            }
            
            response = self.client.post(
                f'/product/{self.test_product_id}/review',
                data=json.dumps(review_data),
                content_type='application/json'
            )
            
            # Review should be accepted
            self.assertIn(response.status_code, [200, 201])

    # ========================
    # TEST PLAN PARTITION: Submit Review Without Rating
    # ========================
    @patch('app.save_review_to_firebase')
    def test_submit_review_without_rating(self, mock_firebase):
        """
        Partition: Submit review without rating
        Input: User enters a review comment but does not select a star rating
        Expected output: Review is not submitted or error message is shown
        Valid: i (Invalid)
        """
        mock_firebase.return_value = True
        
        # Set up session with user_id
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.test_user_id
            sess['email'] = 'reviewuser@gmail.com'
            sess['name'] = 'Review Test User'
        
        # Submit review without rating
        review_data = {
            'review_text': 'Good Product'
            # rating is missing!
        }
        
        response = self.client.post(
            f'/product/{self.test_product_id}/review',
            data=json.dumps(review_data),
            content_type='application/json'
        )
        
        # Should fail - missing rating
        self.assertEqual(response.status_code, 400)

    # ========================
    # TEST PLAN PARTITION: Submit Empty Review
    # ========================
    def test_submit_empty_review_text(self):
        """
        Partition: Submit empty review
        Input: User enters a star rating but leaves review text box empty
        Expected output: Review is not submitted or error message is shown
        Valid: i (Invalid)
        """
        # Set up session with user_id
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.test_user_id
            sess['email'] = 'reviewuser@gmail.com'
            sess['name'] = 'Review Test User'
        
        # Submit review with empty text
        review_data = {
            'rating': 4,
            'review_text': ''  # Empty!
        }
        
        response = self.client.post(
            f'/product/{self.test_product_id}/review',
            data=json.dumps(review_data),
            content_type='application/json'
        )
        
        # Should fail - empty review text
        self.assertEqual(response.status_code, 400)

    # ========================
    # TEST PLAN PARTITION: View Existing Reviews
    # ========================
    @patch('app.save_review_to_firebase')
    def test_view_existing_reviews(self, mock_firebase):
        """
        Partition: View existing reviews
        Input: User opens a product page that already has reviews
        Expected output: Existing reviews are displayed with rating and review text
        Valid: ✓
        """
        mock_firebase.return_value = True
        
        # Set up session with user_id
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.test_user_id
            sess['email'] = 'reviewuser@gmail.com'
            sess['name'] = 'Review Test User'
        
        # Submit a review first
        review_data = {
            'rating': 5,
            'review_text': 'Excellent product!'
        }
        self.client.post(
            f'/product/{self.test_product_id}/review',
            data=json.dumps(review_data),
            content_type='application/json'
        )
        
        # Now retrieve reviews
        response = self.client.get(f'/product/{self.test_product_id}/reviews')
        
        # Should return 200 with at least one review
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data.get('success'))
        self.assertGreater(response_data.get('count', 0), 0)
        self.assertGreater(len(response_data.get('reviews', [])), 0)

    # ========================
    # ADDITIONAL: Rating validation (invalid range)
    # ========================
    def test_review_invalid_rating_out_of_range(self):
        """Test that ratings outside 1-5 range are rejected"""
        # Set up session with user_id
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.test_user_id
            sess['email'] = 'reviewuser@gmail.com'
            sess['name'] = 'Review Test User'
        
        # Try rating of 6 (out of range)
        review_data = {
            'rating': 6,
            'review_text': 'This rating is too high'
        }
        
        response = self.client.post(
            f'/product/{self.test_product_id}/review',
            data=json.dumps(review_data),
            content_type='application/json'
        )
        
        # Should fail - invalid rating
        self.assertEqual(response.status_code, 400)

    # ========================
    # ADDITIONAL: Minimum review text length
    # ========================
    def test_review_minimum_text_length(self):
        """Test that very short review texts are rejected"""
        # Set up session with user_id
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.test_user_id
            sess['email'] = 'reviewuser@gmail.com'
            sess['name'] = 'Review Test User'
        
        # Review text too short (less than 10 chars)
        review_data = {
            'rating': 4,
            'review_text': 'Good'  # Only 4 chars, minimum is 10
        }
        
        response = self.client.post(
            f'/product/{self.test_product_id}/review',
            data=json.dumps(review_data),
            content_type='application/json'
        )
        
        # Should fail - text too short
        self.assertEqual(response.status_code, 400)

    # ========================
    # ADDITIONAL: User not logged in
    # ========================
    def test_submit_review_not_logged_in(self):
        """Test that non-authenticated users cannot submit reviews"""
        review_data = {
            'rating': 5,
            'review_text': 'This should fail - user not logged in'
        }
        
        response = self.client.post(
            f'/product/{self.test_product_id}/review',
            data=json.dumps(review_data),
            content_type='application/json'
        )
        
        # Should fail - not authenticated
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
