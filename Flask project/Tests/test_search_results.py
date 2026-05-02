import unittest
import sys
import os

# Add the Flask project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestSearchResults(unittest.TestCase):
    """Tests for the `search_results.html` route"""

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_search_results_route_renders(self):
        """GET /search-results returns 200 and contains expected elements"""
        response = self.client.get('/search-results')
        self.assertEqual(response.status_code, 200)
        # Page title / heading
        self.assertIn(b'Search Results', response.data)
        # Results container where products are injected by JS
        self.assertIn(b'id="resultsContainer"', response.data)
        # JS fetch to parts API should be referenced in the template script
        self.assertIn(b"/api/parts/all", response.data)


if __name__ == '__main__':
    unittest.main()
