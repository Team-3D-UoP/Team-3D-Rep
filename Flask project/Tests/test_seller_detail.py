import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Flask directory added to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, _get_products_for_seller, _get_reviews_for_seller
from data.sellers import SELLERS_DATA
from data.products import OFFER_PRODUCTS
from data.reviews import REVIEWS_DATA


class TestSellerDetail(unittest.TestCase):
    """Test suite for the seller detail page route and template"""

    def setUp(self):
        """Set up test client before each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up after tests"""
        pass

    def test_seller_detail_template_exists(self):
        """Test that the seller detail template file exists"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'seller_detail.html')
        self.assertTrue(os.path.exists(template_path), "seller_detail.html template file should exist")

    def test_seller_detail_template_is_readable(self):
        """Test that seller_detail.html is readable"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'seller_detail.html')
        self.assertTrue(os.access(template_path, os.R_OK), "Template file should be readable")

    def test_seller_detail_template_encoding(self):
        """Test that seller_detail.html can be read with UTF-8 encoding"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'seller_detail.html')
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                f.read()
            encoding_ok = True
        except UnicodeDecodeError:
            encoding_ok = False
        self.assertTrue(encoding_ok, "Template should be UTF-8 encoded")

    def test_seller_detail_template_file_type(self):
        """Test that seller_detail.html is a file, not a directory"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'seller_detail.html')
        self.assertTrue(os.path.isfile(template_path), "seller_detail.html should be a file, not a directory")

    def test_seller_detail_template_extends_base(self):
        """Test that seller_detail.html extends base.html"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'seller_detail.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn('{% extends "base.html" %}', content, "Template should extend base.html")

    def test_seller_detail_route_loads_successfully(self):
        """Test that the seller detail page loads successfully for valid seller ID"""
        response = self.client.get('/seller/1')
        self.assertEqual(response.status_code, 200)

    def test_seller_detail_route_returns_404_for_invalid_seller(self):
        """Test that the seller detail page returns 404 for invalid seller ID"""
        response = self.client.get('/seller/999')
        self.assertEqual(response.status_code, 404)

    def test_seller_detail_route_response_content_type(self):
        """Test that the seller detail page returns HTML content"""
        response = self.client.get('/seller/1')
        self.assertIn('text/html', response.content_type)

    def test_seller_detail_page_contains_seller_name(self):
        """Test that the seller detail page contains the seller's name"""
        response = self.client.get('/seller/1')
        seller = next((s for s in SELLERS_DATA if s['id'] == 1), None)
        if seller:
            self.assertIn(seller['name'].encode(), response.data)

    def test_seller_detail_page_contains_seller_bio(self):
        """Test that the seller detail page contains the seller's bio"""
        response = self.client.get('/seller/1')
        seller = next((s for s in SELLERS_DATA if s['id'] == 1), None)
        if seller and 'bio' in seller:
            self.assertIn(seller['bio'].encode(), response.data)

    def test_seller_detail_page_contains_rating_info(self):
        """Test that the seller detail page contains rating information"""
        response = self.client.get('/seller/1')
        seller = next((s for s in SELLERS_DATA if s['id'] == 1), None)
        if seller and 'rating' in seller:
            self.assertIn(str(seller['rating']).encode(), response.data)

    def test_seller_detail_page_contains_reviews_section(self):
        """Test that the seller detail page contains a reviews section"""
        response = self.client.get('/seller/1')
        self.assertIn(b'Reviews', response.data)

    def test_seller_detail_page_contains_products_section(self):
        """Test that the seller detail page contains a products section"""
        response = self.client.get('/seller/1')
        self.assertIn(b'Products', response.data)

    def test_seller_detail_template_no_syntax_errors(self):
        """Test that template file can be read without errors"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'seller_detail.html')
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Basic Jinja2 template checks - ensure no unclosed braces
            has_error = (
                content.count('{{') != content.count('}}') or
                content.count('{%') != content.count('%}')
            )
            self.assertFalse(has_error, "Template should have balanced template delimiters")
        except Exception as e:
            self.fail(f"Template should not cause errors when read: {e}")

    def test_seller_detail_no_hardcoded_sensitive_data(self):
        """Test that template doesn't contain hardcoded passwords or secrets"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'seller_detail.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
        
        suspicious_patterns = ['password=', 'secret=', 'api_key=', 'token=']
        found_suspicious = any(pattern in content for pattern in suspicious_patterns)
        self.assertFalse(found_suspicious, "Template should not contain hardcoded secrets")

    def test_sellers_data_has_required_fields(self):
        """Test that all sellers have required fields"""
        required_fields = ['id', 'name', 'rating', 'reviews']
        for seller in SELLERS_DATA:
            for field in required_fields:
                self.assertIn(field, seller, f"Seller {seller.get('id', 'unknown')} missing required field: {field}")

    def test_seller_ids_are_unique(self):
        """Test that all seller IDs are unique"""
        seller_ids = [s['id'] for s in SELLERS_DATA]
        self.assertEqual(len(seller_ids), len(set(seller_ids)), "Seller IDs should be unique")

    def test_get_products_for_seller_function(self):
        """Test that _get_products_for_seller returns products for a valid seller"""
        products = _get_products_for_seller(1)
        self.assertIsInstance(products, list, "_get_products_for_seller should return a list")

    def test_get_reviews_for_seller_function(self):
        """Test that _get_reviews_for_seller returns reviews for a valid seller"""
        reviews = _get_reviews_for_seller(1)
        self.assertIsInstance(reviews, list, "_get_reviews_for_seller should return a list")

    def test_seller_detail_page_title_contains_seller_name(self):
        """Test that the page title contains the seller's name"""
        response = self.client.get('/seller/1')
        seller = next((s for s in SELLERS_DATA if s['id'] == 1), None)
        if seller:
            expected_title = f"{seller['name']} - Team 3D"
            self.assertIn(expected_title.encode(), response.data)


if __name__ == '__main__':
    unittest.main()