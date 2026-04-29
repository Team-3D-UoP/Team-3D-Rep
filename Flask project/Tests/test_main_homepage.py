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