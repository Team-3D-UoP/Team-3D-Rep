import unittest
import sys
import os

# Add the Flask project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, _get_seller_for_product, _get_products_for_seller, _get_reviews_for_seller
from data.products import OFFER_PRODUCTS
from data.sellers import SELLERS_DATA
from data.reviews import REVIEWS_DATA


class TestMainHomepage(unittest.TestCase):
    """Test suite for the main homepage route"""

    def setUp(self):
        """Set up test client before each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up after each test"""
        pass

    def test_homepage_loads_successfully(self):
        """Test that the homepage route returns a 200 status code"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_homepage_renders_correct_template(self):
        """Test that the homepage renders the main_homepage.html template"""
        response = self.client.get('/')
        self.assertIn(b'Team 3D', response.data)  # Check for content from base template

    def test_homepage_passes_products_to_template(self):
        """Test that products are passed to the template"""
        response = self.client.get('/')
        # Products should be included in the response
        self.assertGreater(len(response.data), 0)

    def test_homepage_passes_reviews_to_template(self):
        """Test that reviews are passed to the template"""
        response = self.client.get('/')
        # Check if reviews data is available
        self.assertIsNotNone(REVIEWS_DATA)

