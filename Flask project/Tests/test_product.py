import os
import sys
import unittest

# Add the Flask project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestProductPage(unittest.TestCase):
    """Behavior-oriented tests for the `product.html` page."""

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.response = self.client.get('/product-page')

    def test_product_page_route_renders(self):
        """GET /product-page returns 200 and key shell elements."""
        self.assertEqual(self.response.status_code, 200)
        self.assertIn(b'Product Details - AutoPartFinder', self.response.data)
        self.assertIn(b'id="content"', self.response.data)
        self.assertIn(b'class="loading"', self.response.data)

    def test_product_page_defines_load_product_flow(self):
        """The script should define product id parsing and initial fetch flow."""
        self.assertIn(b'async function loadProduct()', self.response.data)
        self.assertIn(b"const params = new URLSearchParams(window.location.search);", self.response.data)
        self.assertIn(b"let productId = params.get('id');", self.response.data)
        self.assertIn(b"window.location.pathname.split('/')", self.response.data)
        self.assertIn(b"showError('Product not found');", self.response.data)
        self.assertIn(b"showError('Product not found in our database');", self.response.data)
        self.assertIn(b"showError('Could not load products');", self.response.data)
        self.assertIn(b"showError('Error loading product: ' + error.message);", self.response.data)
        self.assertIn(b"fetch(`/api/parts/search`)", self.response.data)
        self.assertIn(b"const product = data.products.find(p => p.id == productId);", self.response.data)

    def test_product_page_defines_display_product_helper(self):
        """The script should define rendering behavior for product details."""
        self.assertIn(b'function displayProduct(product)', self.response.data)
        self.assertIn(b"currentProduct = product;", self.response.data)
        self.assertIn(b"document.getElementById('pageTitle').textContent = product.name + ' - AutoPartFinder';", self.response.data)
        self.assertIn(b"loadReviews(product.id);", self.response.data)

    def test_product_page_includes_seller_conditional_rendering(self):
        """Seller section should be conditionally rendered when seller exists."""
        self.assertIn(b"if (product.seller)", self.response.data)
        self.assertIn(b"const statusClass = product.seller.active ? '' : 'inactive';", self.response.data)
        self.assertIn(b"<div class=\"seller-section\">", self.response.data)
        self.assertIn(b"${product.seller.name}", self.response.data)

    def test_product_page_includes_specs_and_price_fields(self):
        """The details template should render expected pricing and specs fields."""
        self.assertIn(b"${(product.old_price || product.price).toFixed(2)}", self.response.data)
        self.assertIn(b"${(product.price || 0).toFixed(2)}", self.response.data)
        self.assertIn(b"${product.discount_percent || 0}%", self.response.data)
        self.assertIn(b"${product.brand}", self.response.data)
        self.assertIn(b"${product.part_type}", self.response.data)
        self.assertIn(b"${product.year}", self.response.data)
        self.assertIn(b"PART-${product.id}", self.response.data)
        self.assertIn(b"${product.seller ? product.seller.rating : '4.5'}", self.response.data)
        self.assertIn(b"${product.seller ? product.seller.reviews + ' reviews' : 'Not rated'}", self.response.data)

    def test_product_page_defines_reviews_loading_behavior(self):
        """The script should fetch and render reviews with fallback states."""
        self.assertIn(b'async function loadReviews(productId)', self.response.data)
        self.assertIn(b"fetch(`/api/product/${productId}/reviews`)", self.response.data)
        self.assertIn(b"if (data.success && data.reviews && data.reviews.length > 0)", self.response.data)
        self.assertIn(b"'\xe2\x98\x85'.repeat(review.rating)", self.response.data)
        self.assertIn(b"'\xe2\x98\x86'.repeat(5 - review.rating)", self.response.data)
        self.assertIn(b'Loading reviews...', self.response.data)
        self.assertIn(b'No reviews yet. Be the first to review this product!', self.response.data)

    def test_product_page_defines_error_renderer(self):
        """The script should define a dedicated error rendering function."""
        self.assertIn(b'function showError(message)', self.response.data)
        self.assertIn(b'<div class="error">', self.response.data)
        self.assertIn(b'Go Back', self.response.data)

    def test_product_page_defines_add_to_cart_behavior(self):
        """The script should post to cart API and emit cartUpdated on success."""
        self.assertIn(b'async function addToCart(partId)', self.response.data)
        self.assertIn(b"fetch('/api/cart/add'", self.response.data)
        self.assertIn(b"JSON.stringify({ product_id: partId, quantity: 1 })", self.response.data)
        self.assertIn(b"document.dispatchEvent(new Event('cartUpdated'));", self.response.data)
        self.assertIn(b"alert('\xe2\x9c\x93 Added to cart!');", self.response.data)
        self.assertIn(b"alert('Error: ' + (data.error || 'Could not add to cart'));", self.response.data)
        self.assertIn(b"alert('Error adding to cart');", self.response.data)

    def test_product_page_defines_message_seller_behavior(self):
        """The script should guard and message based on current seller state."""
        self.assertIn(b'function messageSeller()', self.response.data)
        self.assertIn(b'if (!currentProduct || !currentProduct.seller)', self.response.data)
        self.assertIn(b'Seller information not available', self.response.data)
        self.assertIn(b'Message feature coming soon!', self.response.data)
        self.assertIn(b'Contact: ${currentProduct.seller.name}', self.response.data)

    def test_product_page_has_navigation_and_action_controls(self):
        """Page shell should include back navigation and action button labels."""
        self.assertIn(b"window.history.back()", self.response.data)
        self.assertIn(b'\xf0\x9f\x9b\x92 Add to Cart', self.response.data)
        self.assertIn(b'\xf0\x9f\x92\xac Message Seller', self.response.data)

    def test_product_page_search_api_dependency_returns_products(self):
        """Dependency API used by loadProduct should return product data."""
        api_response = self.client.get('/api/parts/search')
        self.assertEqual(api_response.status_code, 200)
        payload = api_response.get_json()
        self.assertTrue(payload.get('success'))
        self.assertIn('products', payload)
        self.assertIsInstance(payload['products'], list)
        self.assertGreater(len(payload['products']), 0)

    def test_product_page_wires_domcontentloaded(self):
        """The page should initialize on DOMContentLoaded."""
        self.assertIn(b"window.addEventListener('DOMContentLoaded', loadProduct);", self.response.data)


if __name__ == '__main__':
    unittest.main()
