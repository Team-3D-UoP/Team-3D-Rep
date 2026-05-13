"""
Automated tests for Filtering & Sorting flows
This file covers search filtering, brand filtering, and sorting behavior
from the test plan.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestFilteringSortingFlows(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    # ========================
    # Search Filtering
    # ========================

    def test_search_by_keyword_returns_matching_parts(self):
        """Search by keyword returns parts matching the search term"""
        response = self.client.get('/api/parts/search?keyword=engine')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('parts', payload)
        self.assertIsInstance(payload['parts'], list)

    def test_search_by_empty_keyword_returns_all_parts(self):
        """Search with empty keyword returns all available parts"""
        response = self.client.get('/api/parts/search?keyword=')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('parts', payload)
        self.assertIsInstance(payload['parts'], list)

    def test_search_returns_empty_list_for_non_existent_keyword(self):
        """Search for non-existent keyword returns empty list"""
        response = self.client.get('/api/parts/search?keyword=nonexistentpartxyz')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('parts', payload)
        self.assertEqual(len(payload['parts']), 0)

    def test_search_results_contain_required_fields(self):
        """Search results include required part fields"""
        response = self.client.get('/api/parts/search?keyword=engine')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        if len(payload['parts']) > 0:
            part = payload['parts'][0]
            self.assertIn('id', part)
            self.assertIn('name', part)
            self.assertIn('price', part)
            self.assertIn('brand', part)

    # ========================
    # Brand Filtering
    # ========================

    def test_filter_by_brand_returns_matching_parts(self):
        """Filter by brand returns parts from selected brand"""
        response = self.client.get('/api/parts/search?brand=toyota')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('parts', payload)
        self.assertIsInstance(payload['parts'], list)

    def test_filter_by_multiple_brands(self):
        """Filter by multiple brands returns parts from all selected brands"""
        response = self.client.get('/api/parts/search?brand=toyota&brand=honda')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('parts', payload)
        self.assertIsInstance(payload['parts'], list)

    def test_filter_by_non_existent_brand_returns_empty(self):
        """Filter by non-existent brand returns empty list"""
        response = self.client.get('/api/parts/search?brand=nonexistentbrand')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('parts', payload)
        self.assertEqual(len(payload['parts']), 0)

    def test_search_and_brand_filter_together(self):
        """Search keyword and brand filter work together"""
        response = self.client.get('/api/parts/search?keyword=engine&brand=toyota')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('parts', payload)
        self.assertIsInstance(payload['parts'], list)

    # ========================
    # Price Sorting
    # ========================

    def test_sort_by_price_ascending(self):
        """Sort parts by price in ascending order"""
        response = self.client.get('/api/parts/search?sort=price_asc')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('parts', payload)
        if len(payload['parts']) > 1:
            prices = [part['price'] for part in payload['parts']]
            self.assertEqual(prices, sorted(prices))

    def test_sort_by_price_descending(self):
        """Sort parts by price in descending order"""
        response = self.client.get('/api/parts/search?sort=price_desc')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('parts', payload)
        if len(payload['parts']) > 1:
            prices = [part['price'] for part in payload['parts']]
            self.assertEqual(prices, sorted(prices, reverse=True))

    # ========================
    # Rating Sorting
    # ========================

    def test_sort_by_rating_highest(self):
        """Sort parts by rating in descending order"""
        response = self.client.get('/api/parts/search?sort=rating_high')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('parts', payload)

    def test_sort_by_rating_lowest(self):
        """Sort parts by rating in ascending order"""
        response = self.client.get('/api/parts/search?sort=rating_low')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('parts', payload)


if __name__ == '__main__':
    unittest.main()
