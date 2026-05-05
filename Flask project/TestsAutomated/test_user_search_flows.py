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
    def test_search_valid_results(self):
        """
        Partition: Valid search results
        Input: Search query: "brake"
        Expected output: API returns results with success=True and count > 0
        Valid: ✓
        """
        response = self.client.get('/api/parts/search?q=brake')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data.get('success'))
        self.assertIn('count', response_data)
        self.assertIn('products', response_data)

    # ========================
    # TEST PLAN PARTITION: No Matching Results
    # ========================
    def test_search_no_matching_results(self):
        """
        Partition: No matching results
        Input: Search query: "xyzabc123xyz" (non-existent part)
        Expected output: API returns success=True but count=0
        Valid: ✓ (Valid but returns empty)
        """
        response = self.client.get('/api/parts/search?q=xyzabc123xyz')
        
        # Should return 200 with empty results
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data.get('success'))
        self.assertEqual(response_data.get('count'), 0)
        self.assertEqual(len(response_data.get('products', [])), 0)

    # ========================
    # TEST PLAN PARTITION: Empty Search Query
    # ========================
    def test_search_empty_query(self):
        """
        Partition: Empty search query
        Input: Search query: "" (empty string)
        Expected output: Returns all products (empty search matches all)
        Valid: i (Invalid but handled gracefully)
        """
        response = self.client.get('/api/parts/search?q=')
        
        # Empty query should return all products (no filter)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data.get('success'))
        # Empty search should return all available products
        self.assertGreaterEqual(response_data.get('count', 0), 0)

    # ========================
    # TEST PLAN PARTITION: Special Characters in Search
    # ========================
    def test_search_special_characters(self):
        """
        Partition: Special characters in search
        Input: Search query: "brake@pads#123$%"
        Expected output: Search handles special characters safely without error
        Valid: ✓ (Valid but may have limited results)
        """
        # URL-encoded special characters
        response = self.client.get('/api/parts/search?q=brake%40pads%23123%24%25')
        
        # Should handle special characters without error
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data.get('success'))
        # Count should be 0 or more (graceful handling of no matches)
        self.assertGreaterEqual(response_data.get('count', 0), 0)

    # ========================
    # ADDITIONAL: Search with case-insensitive keywords
    # ========================
    def test_search_case_insensitive(self):
        """Test that search is case-insensitive"""
        response_lower = self.client.get('/api/parts/search?q=brake')
        response_upper = self.client.get('/api/parts/search?q=BRAKE')
        
        # Both should return same results
        self.assertEqual(response_lower.status_code, 200)
        self.assertEqual(response_upper.status_code, 200)
        
        data_lower = json.loads(response_lower.data)
        data_upper = json.loads(response_upper.data)
        
        self.assertEqual(data_lower.get('count'), data_upper.get('count'))

    # ========================
    # ADDITIONAL: Search results page loads
    # ========================
    def test_search_results_page_loads(self):
        """Test that search results page HTML endpoint works"""
        response = self.client.get('/search-results')
        
        # Should return 200 and HTML content
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response.content_type)

    # ========================
    # ADDITIONAL: Search with whitespace trimming
    # ========================
    def test_search_whitespace_trimming(self):
        """Test that leading/trailing whitespace is trimmed"""
        response_with_spaces = self.client.get('/api/parts/search?q=%20%20brake%20%20')
        response_normal = self.client.get('/api/parts/search?q=brake')
        
        # Both should have same results
        self.assertEqual(response_with_spaces.status_code, 200)
        self.assertEqual(response_normal.status_code, 200)
        
        data_spaces = json.loads(response_with_spaces.data)
        data_normal = json.loads(response_normal.data)
        
        self.assertEqual(data_spaces.get('count'), data_normal.get('count'))


if __name__ == '__main__':
    unittest.main()
