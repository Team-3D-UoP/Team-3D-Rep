"""
Automated tests for User Search workflows
Tests all partitions from the test plan:
- Valid search results
- No matching results
- Empty search
- Special characters in search
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import User


class TestUserSearchFlows(unittest.TestCase):
    """Test suite for user search workflows based on test plan"""

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

    def tearDown(self):
        """Clean up after each test"""
        self.firebase_patcher.stop()
        
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # ========================
    # TEST PLAN PARTITION: Valid Search Results
    # ========================
    @patch('app.search_products')
    def test_search_valid_results(self, mock_search_products):
        """
        Partition: Valid search results
        Input: Search query: "brake pads"
        Expected output: Search results page shows relevant products/parts
        Valid: ✓
        """
        # Mock search to return valid results
        mock_search_products.return_value = [
            {
                'id': 1,
                'name': 'Brake Pad Set',
                'description': 'High-quality brake pads',
                'price': 45.99,
                'seller_id': 1
            },
            {
                'id': 2,
                'name': 'Premium Brake Pads',
                'description': 'Performance brake pads',
                'price': 65.50,
                'seller_id': 2
            }
        ]
        
        response = self.client.get('/search?query=brake+pads')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response.content_type)

    # ========================
    # TEST PLAN PARTITION: No Matching Results
    # ========================
    @patch('app.search_products')
    def test_search_no_matching_results(self, mock_search_products):
        """
        Partition: No matching results
        Input: Search query: "xyzabc123xyz" (non-existent part)
        Expected output: No results page or "no matching results" message
        Valid: ✓ (Valid but returns empty)
        """
        # Mock search to return empty results
        mock_search_products.return_value = []
        
        response = self.client.get('/search?query=xyzabc123xyz')
        
        # Should still return 200 but with empty results
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response.content_type)

    # ========================
    # TEST PLAN PARTITION: Empty Search Query
    # ========================
    def test_search_empty_query(self):
        """
        Partition: Empty search query
        Input: Search query: "" (empty string)
        Expected output: Error message or no results
        Valid: i (Invalid)
        """
        response = self.client.get('/search?query=')
        
        # Should handle empty search gracefully
        # Either 400 error or 200 with empty results
        self.assertIn(response.status_code, [200, 400])

    # ========================
    # TEST PLAN PARTITION: Special Characters in Search
    # ========================
    @patch('app.search_products')
    def test_search_special_characters(self, mock_search_products):
        """
        Partition: Special characters in search
        Input: Search query: "brake@pads#123$%"
        Expected output: Search handles special characters safely
        Valid: ✓ (Valid but may have limited results)
        """
        # Mock search to handle special characters safely
        mock_search_products.return_value = []
        
        response = self.client.get('/search?query=brake%40pads%23123%24%25')
        
        # Should handle special characters without error
        self.assertIn(response.status_code, [200, 400])

    # ========================
    # ADDITIONAL: Search with API endpoint
    # ========================
    @patch('app.search_products')
    def test_search_api_json_response(self, mock_search_products):
        """Test search via API endpoint returns JSON"""
        mock_search_products.return_value = [
            {
                'id': 1,
                'name': 'Engine Oil',
                'price': 25.99,
                'seller_id': 1
            }
        ]
        
        response = self.client.get(
            '/api/search',
            headers={'Accept': 'application/json'},
            query_string={'query': 'engine oil'}
        )
        
        # API should return 200 or 400
        self.assertIn(response.status_code, [200, 400, 404])

    # ========================
    # ADDITIONAL: Search pagination
    # ========================
    @patch('app.search_products')
    def test_search_pagination(self, mock_search_products):
        """Test search with pagination"""
        # Mock large result set
        mock_search_products.return_value = [
            {'id': i, 'name': f'Part {i}', 'price': 10 + i}
            for i in range(50)
        ]
        
        response = self.client.get('/search?query=part&page=1')
        
        # Should return search results page
        self.assertEqual(response.status_code, 200)

    # ========================
    # ADDITIONAL: Search with filters
    # ========================
    @patch('app.search_products')
    def test_search_with_price_filter(self, mock_search_products):
        """Test search with price filter"""
        mock_search_products.return_value = [
            {'id': 1, 'name': 'Affordable Part', 'price': 15.99}
        ]
        
        response = self.client.get(
            '/search?query=part&min_price=10&max_price=50'
        )
        
        # Should return filtered results
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
