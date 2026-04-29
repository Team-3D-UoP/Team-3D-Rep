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

    def test_homepage_response_content_type(self):
        """Test that the homepage returns HTML content"""
        response = self.client.get('/')
        self.assertIn('text/html', response.content_type)

    def test_all_products_have_required_fields(self):
        """Test that all products have required fields (id, name, price)"""
        required_fields = ['id', 'name', 'price']
        for product in OFFER_PRODUCTS:
            for field in required_fields:
                self.assertIn(field, product, f"Product missing required field: {field}")

    def test_product_ids_are_unique(self):
        """Test that all product IDs are unique"""
        product_ids = [p['id'] for p in OFFER_PRODUCTS]
        self.assertEqual(len(product_ids), len(set(product_ids)),
                        "Product IDs should be unique")

    def test_product_ids_are_positive_integers(self):
        """Test that all product IDs are positive integers"""
        for product in OFFER_PRODUCTS:
            self.assertIsInstance(product['id'], int)
            self.assertGreater(product['id'], 0)

    def test_product_names_are_non_empty(self):
        """Test that all product names are non-empty strings"""
        for product in OFFER_PRODUCTS:
            self.assertIsInstance(product['name'], str)
            self.assertGreater(len(product['name']), 0)
