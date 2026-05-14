"""
Automated tests for Product flows
This file will cover product detail page API behavior
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestProductFlows(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_get_product_details_valid_id(self):
        """Get product details for a valid product ID"""
        response = self.client.get('/product/1001')
        self.assertEqual(response.status_code, 200)
        # Check that product data is rendered in the template
        data = response.get_data(as_text=True)
        self.assertIn('Pressure Washer', data)
        self.assertIn('CarCare Pro', data)

    def test_get_product_details_invalid_id(self):
        """Get product details for an invalid product ID"""
        response = self.client.get('/product/9999')
        self.assertEqual(response.status_code, 404)

    def test_get_product_details_negative_id(self):
        """Get product details for a negative product ID"""
        response = self.client.get('/product/-1')
        self.assertEqual(response.status_code, 404)

    def test_get_product_reviews_endpoint(self):
        """Get reviews for a specific product"""
        response = self.client.get('/product/1001/reviews')
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn('reviews', payload)
        self.assertIsInstance(payload['reviews'], list)

    def test_post_product_review_requires_auth(self):
        """Posting a product review requires authentication"""
        response = self.client.post('/product/1001/review', json={
            'rating': 5,
            'review_text': 'Great product!'
        })
        # Should redirect to login or return error
        self.assertIn(response.status_code, [302, 401])

    def test_delete_product_review_requires_auth(self):
        """Deleting a product review requires authentication"""
        response = self.client.delete('/product/1001/review/1')
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()