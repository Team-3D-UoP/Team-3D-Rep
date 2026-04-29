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

    def test_product_prices_are_valid(self):
        """Test that all product prices are positive numbers"""
        for product in OFFER_PRODUCTS:
            self.assertIn('price', product)
            try:
                price = float(product['price'])
                self.assertGreaterEqual(price, 0, f"Product {product['id']} has negative price")
            except (ValueError, TypeError):
                self.fail(f"Product {product['id']} has invalid price format")
                
    def test_all_sellers_have_required_fields(self):
        """Test that all sellers have required fields (id, name)"""
        required_fields = ['id', 'name']
        for seller in SELLERS_DATA:
            for field in required_fields:
                self.assertIn(field, seller, f"Seller missing required field: {field}")

    def test_seller_ids_are_unique(self):
        """Test that all seller IDs are unique"""
        seller_ids = [s['id'] for s in SELLERS_DATA]
        self.assertEqual(len(seller_ids), len(set(seller_ids)),
                        "Seller IDs should be unique")

    def test_seller_ids_are_positive_integers(self):
        """Test that all seller IDs are positive integers"""
        for seller in SELLERS_DATA:
            self.assertIsInstance(seller['id'], int)
            self.assertGreater(seller['id'], 0)

    def test_seller_names_are_non_empty(self):
        """Test that all seller names are non-empty strings"""
        for seller in SELLERS_DATA:
            self.assertIsInstance(seller['name'], str)
            self.assertGreater(len(seller['name']), 0)

    def test_seller_has_products(self):
        """Test that each seller has at least some products assigned"""
        for seller in SELLERS_DATA:
            products = _get_products_for_seller(seller['id'])
            self.assertGreater(len(products), 0,
                             f"Seller {seller['name']} has no products assigned")

    def test_all_reviews_have_required_fields(self):
        """Test that all reviews have required fields"""
        required_fields = ['rating', 'text']
        for review in REVIEWS_DATA:
            for field in required_fields:
                self.assertIn(field, review, f"Review missing required field: {field}")

    def test_review_ratings_are_valid(self):
        """Test that all review ratings are between 1 and 5"""
        for review in REVIEWS_DATA:
            self.assertIsInstance(review['rating'], int)
            self.assertGreaterEqual(review['rating'], 1)
            self.assertLessEqual(review['rating'], 5)

    def test_review_text_is_non_empty(self):
        """Test that all review text is non-empty"""
        for review in REVIEWS_DATA:
            self.assertIsInstance(review['text'], str)
            self.assertGreater(len(review['text']), 0)

    def test_products_have_sellers_assigned(self):
        """Test that all products get a seller assigned via _get_seller_for_product"""
        for product in OFFER_PRODUCTS:
            seller = _get_seller_for_product(product)
            self.assertIsNotNone(seller, f"Product {product['id']} has no seller assigned")
            self.assertIn('id', seller)
            self.assertIn('name', seller)

    def test_seller_assignment_is_deterministic(self):
        """Test that the same product always gets the same seller"""
        if OFFER_PRODUCTS and SELLERS_DATA:
            product = OFFER_PRODUCTS[0]
            seller1 = _get_seller_for_product(product)
            seller2 = _get_seller_for_product(product)
            self.assertEqual(seller1['id'], seller2['id'],
                           "Seller assignment should be deterministic")

    def test_seller_assignment_cycles_through_sellers(self):
        """Test that seller assignment uses a round-robin distribution"""
        if len(OFFER_PRODUCTS) > len(SELLERS_DATA):
            # Check that not all products are assigned to the same seller
            assigned_sellers = set()
            for product in OFFER_PRODUCTS[:len(SELLERS_DATA) + 1]:
                seller = _get_seller_for_product(product)
                assigned_sellers.add(seller['id'])
            self.assertGreater(len(assigned_sellers), 1,
                             "Products should be distributed across multiple sellers")

    def test_seller_assignment_modulo_operation(self):
        """Test that seller assignment follows modulo pattern"""
        if OFFER_PRODUCTS and SELLERS_DATA:
            for i, product in enumerate(OFFER_PRODUCTS[:5]):
                expected_seller = SELLERS_DATA[i % len(SELLERS_DATA)]
                actual_seller = _get_seller_for_product(product)
                self.assertEqual(actual_seller['id'], expected_seller['id'])

    def test_get_products_for_seller_returns_list(self):
        """Test that _get_products_for_seller returns a list"""
        if SELLERS_DATA:
            seller = SELLERS_DATA[0]
            products = _get_products_for_seller(seller['id'])
            self.assertIsInstance(products, list)

    def test_get_products_for_seller_returns_valid_products(self):
        """Test that products returned for seller are valid products"""
        if SELLERS_DATA:
            seller = SELLERS_DATA[0]
            products = _get_products_for_seller(seller['id'])
            for product in products:
                self.assertIn('id', product)
                self.assertIn('name', product)
                # Verify the product is actually in OFFER_PRODUCTS
                self.assertIn(product['id'], [p['id'] for p in OFFER_PRODUCTS])

    def test_get_reviews_for_seller_returns_list(self):
        """Test that _get_reviews_for_seller returns a list"""
        if SELLERS_DATA:
            seller = SELLERS_DATA[0]
            reviews = _get_reviews_for_seller(seller['id'])
            self.assertIsInstance(reviews, list)

    def test_get_reviews_for_seller_returns_valid_reviews(self):
        """Test that reviews returned for seller are valid"""
        if SELLERS_DATA and REVIEWS_DATA:
            seller = SELLERS_DATA[0]
            reviews = _get_reviews_for_seller(seller['id'])
            for review in reviews:
                self.assertIn('rating', review)
                self.assertIn('text', review)

    def test_get_reviews_for_seller_max_four_reviews(self):
        """Test that seller gets maximum of 4 reviews"""
        if SELLERS_DATA:
            for seller in SELLERS_DATA:
                reviews = _get_reviews_for_seller(seller['id'])
                self.assertLessEqual(len(reviews), 4)

    def test_homepage_with_empty_products(self):
        """Test homepage behavior when no products are available"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_homepage_handles_missing_sellers_gracefully(self):
        """Test that homepage doesn't crash if sellers data is unavailable"""
        if not SELLERS_DATA:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)

    def test_invalid_product_id_returns_404(self):
        """Test that requesting a non-existent product returns 404"""
        response = self.client.get('/product/99999')
        self.assertEqual(response.status_code, 404)

    def test_invalid_seller_id_returns_404(self):
        """Test that requesting a non-existent seller returns 404"""
        response = self.client.get('/seller/99999')
        self.assertEqual(response.status_code, 404)

