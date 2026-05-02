import os
import sys
import unittest

from flask import render_template

# Add the Flask project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestProductDetailPageTemplate(unittest.TestCase):
    """Behavior-oriented tests for `product_detail_page.html`."""

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.product = {
            'id': 1,
            'name': 'Toyota Oil Filter',
            'brand': 'Toyota',
            'part_type': 'Oil Filter',
            'year': '2026',
            'price': 27,
            'old_price': 30,
            'discount_percent': 10,
            'description': 'Toyota oil filter',
            'image': 'product.jpg',
            'seller': {
                'id': 11,
                'name': 'AutoParts Seller',
                'title': 'Verified Seller',
                'pfp': 'A',
                'rating': 4.5,
                'reviews': 128,
                'response_time': '2 hours',
                'active': True,
            },
        }

    def render_page(self, product):
        with self.app.test_request_context('/'):
            return render_template('product_detail_page.html', product=product)

    def test_template_renders_core_product_structure(self):
        """The template should render the page shell and key product fields."""
        html = self.render_page(self.product)
        self.assertIn('Product Details - AutoPartFinder', html)
        self.assertIn('breadcrumbProduct', html)
        self.assertIn('productContainer', html)
        self.assertIn('Toyota Oil Filter', html)
        self.assertIn('£27', html)
        self.assertIn('Save 10%', html)

    def test_template_renders_breadcrumb_navigation(self):
        """The breadcrumb should include home and search-results navigation text."""
        html = self.render_page(self.product)
        self.assertIn("window.location.href='/'", html)
        self.assertIn('window.history.back()', html)
        self.assertIn('Search Results', html)

    def test_template_contains_loading_and_error_shells(self):
        """The page should include loading and error state containers."""
        html = self.render_page(self.product)
        self.assertIn('class="loading"', html)
        self.assertIn('class="error-message"', html)
        self.assertIn('loading::after', html)
        self.assertIn('Go Back', html)

    def test_template_defines_load_product_flow(self):
        """The page script should load product data from the API."""
        html = self.render_page(self.product)
        self.assertIn('const urlParams = new URLSearchParams(window.location.search);', html)
        self.assertIn('const productId = urlParams.get(\'id\');', html)
        self.assertIn('async function loadProduct()', html)
        self.assertIn('fetch(`/api/parts/${productId}`)', html)
        self.assertIn("showError('Product ID not found')", html)
        self.assertIn("showError('Product not found')", html)

    def test_template_defines_display_and_error_states(self):
        """The page should define the displayProduct and showError flows."""
        html = self.render_page(self.product)
        self.assertIn('function displayProduct(product)', html)
        self.assertIn('document.getElementById(\'breadcrumbProduct\').textContent = product.name;', html)
        self.assertIn('function showError(message)', html)
        self.assertIn('Product ID not found', html)
        self.assertIn('Error loading product:', html)
        self.assertIn('Go Back', html)

    def test_template_handles_missing_product_id(self):
        """The loadProduct flow should guard against a missing productId."""
        html = self.render_page(self.product)
        self.assertIn("if (!productId)", html)
        self.assertIn("showError('Product ID not found')", html)

    def test_template_handles_api_failure_states(self):
        """The loadProduct flow should include API success and failure branches."""
        html = self.render_page(self.product)
        self.assertIn('if (data.success)', html)
        self.assertIn("showError('Product not found')", html)
        self.assertIn("showError('Error loading product: ' + error.message)", html)

    def test_template_defines_seller_section_behavior(self):
        """A seller should render the seller card and action buttons."""
        html = self.render_page(self.product)
        self.assertIn('Sold by', html)
        self.assertIn('seller-card', html)
        self.assertIn('seller-avatar', html)
        self.assertIn('seller-basic-info', html)
        self.assertIn("contactSeller('${product.seller.id}')", html)
        self.assertIn("viewSellerStore('${product.seller.id}')", html)

    def test_template_renders_not_rated_fallback_without_seller(self):
        """When no seller is provided, the template should keep the not-rated fallback text."""
        product = dict(self.product)
        product.pop('seller')
        html = self.render_page(product)
        self.assertIn('Not rated', html)
        self.assertNotIn('Sold by', html)
        self.assertNotIn('seller-card', html)

    def test_template_includes_product_spec_fields(self):
        """The rendered page should expose the expected product spec labels and values."""
        html = self.render_page(self.product)
        self.assertIn('Brand', html)
        self.assertIn('Part Type', html)
        self.assertIn('Year', html)
        self.assertIn('SKU', html)
        self.assertIn('PART-1', html)

    def test_template_hides_seller_card_when_missing(self):
        """A product without seller data should skip the seller card block."""
        product = dict(self.product)
        product.pop('seller')
        html = self.render_page(product)
        self.assertNotIn('Sold by', html)
        self.assertNotIn('seller-card', html)

    def test_template_defines_action_behaviors(self):
        """Add to cart and wishlist actions should be wired in the script."""
        html = self.render_page(self.product)
        self.assertIn('async function addToCart(partId)', html)
        self.assertIn("fetch('/api/cart'", html)
        self.assertIn("document.dispatchEvent(new Event('cartUpdated'));", html)
        self.assertIn('function addToWishlist(partId)', html)
        self.assertIn('Added to wishlist! (Feature coming soon)', html)
        self.assertIn('function contactSeller(sellerId)', html)
        self.assertIn('Contact form coming soon!', html)
        self.assertIn("alert('Error: ' + (data.error || 'Unknown error'))", html)
        self.assertIn("alert('Error adding to cart')", html)

    def test_template_defines_review_fallback_text(self):
        """The template should expose the review list fallback and button controls."""
        html = self.render_page(self.product)
        self.assertIn('Loading reviews...', html)
        self.assertIn('No reviews yet. Be the first to review!', html)
        self.assertIn('deleteReview(review.id)', html)

    def test_template_defines_media_queries(self):
        """Responsive rules should be present for narrow screens."""
        html = self.render_page(self.product)
        self.assertIn('@media (max-width: 768px)', html)
        self.assertIn('.product-main {', html)
        self.assertIn('.seller-stats {', html)

    def test_template_defines_navigation_behavior(self):
        """Seller store navigation should point to the seller page."""
        html = self.render_page(self.product)
        self.assertIn('function viewSellerStore(sellerId)', html)
        self.assertIn('window.location.href = `/seller/${sellerId}`;', html)
        self.assertIn("window.addEventListener('DOMContentLoaded', loadProduct);", html)


if __name__ == '__main__':
    unittest.main()
