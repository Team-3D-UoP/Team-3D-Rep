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
        self.response = self.client.get('/search-results')

    def test_search_results_route_renders(self):
        """GET /search-results returns 200 and contains expected elements"""
        self.assertEqual(self.response.status_code, 200)
        self.assertIn(b'Search Results', self.response.data)
        self.assertIn(b'id="resultsContainer"', self.response.data)

    def test_search_results_page_defines_init_flow(self):
        """The page script should define the initialization flow."""
        self.assertIn(b"const searchParams = new URLSearchParams(window.location.search);", self.response.data)
        self.assertIn(b"const searchQuery = searchParams.get('q') || '';", self.response.data)
        self.assertIn(b'async function init()', self.response.data)
        self.assertIn(b'await searchProducts();', self.response.data)
        self.assertIn(b'await loadBrands();', self.response.data)
        self.assertIn(b'setupFilterListeners();', self.response.data)

    def test_search_results_page_defines_search_and_display_helpers(self):
        """The page script should define the search and rendering helpers."""
        self.assertIn(b'async function searchProducts()', self.response.data)
        self.assertIn(b'function displayProducts(products)', self.response.data)
        self.assertIn(b'function loadBrands()', self.response.data)
        self.assertIn(b"const endpoint = searchQuery", self.response.data)
        self.assertIn(b"displayProducts(allProducts);", self.response.data)

    def test_search_results_page_defines_filter_helpers(self):
        """The page script should define the filter control helpers."""
        self.assertIn(b'function setupFilterListeners()', self.response.data)
        self.assertIn(b'function applyFilters()', self.response.data)
        self.assertIn(b'function resetFilters()', self.response.data)
        self.assertIn(b"document.getElementById('priceFilter').addEventListener('input'", self.response.data)
        self.assertIn(b"document.getElementById('brandFilter').addEventListener('change', applyFilters);", self.response.data)

    def test_search_results_page_defines_cart_and_navigation_helpers(self):
        """The page script should define cart and navigation helpers."""
        self.assertIn(b'async function addToCart(partId)', self.response.data)
        self.assertIn(b'function viewDetails(partId)', self.response.data)
        self.assertIn(b"document.dispatchEvent(new Event('cartUpdated'));", self.response.data)
        self.assertIn(b"window.location.href = `/product/${partId}`;", self.response.data)

    def test_search_results_page_uses_expected_api_endpoints(self):
        """The page script should call the expected parts APIs."""
        self.assertIn(b"/api/parts/search?q=", self.response.data)
        self.assertIn(b"/api/parts/all", self.response.data)
        self.assertIn(b"/api/parts/brands", self.response.data)
        self.assertIn(b"fetch('/api/cart'", self.response.data)

    def test_search_results_page_has_expected_filters(self):
        """The page should expose the search filters used by the JavaScript."""
        self.assertIn(b'id="brandFilter"', self.response.data)
        self.assertIn(b'id="itemTypeFilter"', self.response.data)
        self.assertIn(b'id="yearFilter"', self.response.data)
        self.assertIn(b'id="priceFilter"', self.response.data)
        self.assertIn(b'id="priceValue"', self.response.data)

    def test_search_results_page_wires_domcontentloaded_initialization(self):
        """The page should initialize itself after DOMContentLoaded."""
        self.assertIn(b"window.addEventListener('DOMContentLoaded', init);", self.response.data)

    def test_search_results_page_handles_no_results_state(self):
        """The template should include the fallback message for empty result sets."""
        self.assertIn(b'No results found', self.response.data)
        self.assertIn(b'Try searching with different keywords or browse all parts.', self.response.data)
        self.assertIn(b'No products match your filters', self.response.data)

    def test_search_results_page_handles_error_state(self):
        """The template should include the fallback message for fetch errors."""
        self.assertIn(b'Error loading results', self.response.data)
        self.assertIn(b'${error.message}', self.response.data)

    def test_search_results_page_defines_product_card_click_behavior(self):
        """Product cards should be wired to navigate to the detail page."""
        self.assertIn(b"document.addEventListener('click', function(e) {", self.response.data)
        self.assertIn(b"e.target.closest('.product-card')", self.response.data)
        self.assertIn(b"viewDetails(productId);", self.response.data)

    def test_search_results_page_renders_product_fields(self):
        """The product card template should render the expected product fields."""
        self.assertIn(b'${product.brand}', self.response.data)
        self.assertIn(b'${product.name}', self.response.data)
        self.assertIn(b'${product.description}', self.response.data)
        self.assertIn(b'${product.price}', self.response.data)
        self.assertIn(b'${product.old_price || product.price}', self.response.data)
        self.assertIn(b'${product.discount_percent || 0}%', self.response.data)


if __name__ == '__main__':
    unittest.main()
