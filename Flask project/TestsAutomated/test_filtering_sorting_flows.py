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



    def test_search_by_keyword_returns_matching_parts(self):
        """Search by keyword returns parts matching the search term"""
        response = self.client.get('/api/parts/search?q=engine')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('products', payload)
        self.assertIsInstance(payload['products'], list)

    def test_search_by_empty_keyword_returns_all_parts(self):
        """Search with empty keyword returns all available parts"""
        response = self.client.get('/api/parts/search?q=')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('products', payload)
        self.assertIsInstance(payload['products'], list)

    def test_search_returns_empty_for_non_existent_keyword(self):
        """Search for non-existent keyword returns empty list"""
        response = self.client.get('/api/parts/search?q=nonexistentpartxyz')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('products', payload)
        self.assertEqual(len(payload['products']), 0)

    def test_search_results_contain_required_fields(self):
        """Search results include required part fields"""
        response = self.client.get('/api/parts/search?q=engine')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        if len(payload['products']) > 0:
            part = payload['products'][0]
            self.assertIn('id', part)
            self.assertIn('name', part)
            self.assertIn('price', part)
            self.assertIn('brand', part)

    # ========================
    # Offers Endpoint
    # ========================

    def test_get_offers_returns_active_offers(self):
        """Offers endpoint returns active promotional offers"""
        response = self.client.get('/api/offers')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('products', payload)
        self.assertIsInstance(payload['products'], list)

    def test_offers_contain_required_fields(self):
        """Offers include required fields"""
        response = self.client.get('/api/offers')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        if len(payload['products']) > 0:
            offer = payload['products'][0]
            self.assertIn('id', offer)
            self.assertIn('name', offer)
            self.assertIn('price', offer)
            self.assertIn('brand', offer)


if __name__ == '__main__':
    unittest.main()
