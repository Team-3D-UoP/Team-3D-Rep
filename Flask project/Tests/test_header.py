import os
import sys
import unittest

# Ensure project root is on sys.path so imports like `from app import app` work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class HeaderTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_header_renders_on_home_page(self):
        rv = self.client.get('/')
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode('utf-8')
        # Header should be included via base.html
        self.assertIn('id="commonHeader"', data)

    def test_header_contains_logo_and_branding(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for logo image and alt text
            self.assertIn('autoPartFinderLogo.png', data)
            self.assertIn('AutoPartFinder logo', data)
            self.assertIn('AutoPartFinder', data)

    def test_header_contains_navigation_buttons(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for Home and Account buttons
            self.assertIn('class="headerButton"', data)
            self.assertIn('Home</a>', data)
            self.assertIn('Account</a>', data)

    def test_header_contains_search_input(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for search input field
            self.assertIn('id="headerSearch"', data)
            self.assertIn('Search car parts...', data)
            self.assertIn('placeholder=', data)

    def test_header_contains_search_button(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for search button
            self.assertIn('id="searchBtn"', data)
            self.assertIn('<button id="searchBtn"', data)

    def test_header_contains_search_dropdown(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for search dropdown container
            self.assertIn('id="searchDropdown"', data)
            self.assertIn('class="search-dropdown"', data)

    def test_header_contains_burger_button(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for burger menu button
            self.assertIn('id="burgerButton"', data)
            self.assertIn('onclick="hideBurger()"', data)

    def test_header_contains_burger_menu(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for burger menu container
            self.assertIn('id="burgerMenu"', data)
            self.assertIn('id="headerAccounts"', data)

    def test_header_burger_menu_items(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for menu items in burger menu
            self.assertIn('Jump to another page', data)
            self.assertIn('Account</a>', data)
            self.assertIn('Orders</a>', data)
            self.assertIn('Car Registration', data)
            self.assertIn('Part Registration', data)
            self.assertIn('Admin Login', data)

    def test_header_contains_hide_burger_function(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for burger toggle function
            self.assertIn('function hideBurger()', data)
            self.assertIn('burgerMenu.hidden = !burgerMenu.hidden', data)

    def test_header_contains_search_functionality(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for search event listeners and functions
            self.assertIn('addEventListener(\'input\'', data)
            self.assertIn('addEventListener(\'keypress\'', data)
            self.assertIn('addEventListener(\'click\'', data)
            self.assertIn('goToSearchResults', data)

    def test_header_contains_live_search_api_call(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for live search API endpoint reference
            self.assertIn('/api/parts/search', data)
            self.assertIn('encodeURIComponent', data)

    def test_header_contains_debounce_search(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for search debouncing (300ms timeout)
            self.assertIn('clearTimeout(searchTimeout)', data)
            self.assertIn('setTimeout', data)
            self.assertIn('300', data)

    def test_header_contains_search_result_display_function(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for result display function
            self.assertIn('function displaySearchResults(products)', data)
            self.assertIn('search-result-item', data)
            self.assertIn('search-result-price', data)
            self.assertIn('search-result-seller', data)

    def test_header_contains_product_detail_navigation(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for product detail navigation
            self.assertIn('function viewProductDetail(productId)', data)
            self.assertIn('/product/', data)

    def test_header_contains_search_error_handling(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for error handling in search
            self.assertIn('catch (error)', data)
            self.assertIn('search-error', data)
            self.assertIn('search-no-results', data)

    def test_header_contains_cart_count_function(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for cart count update function
            self.assertIn('function updateCartCount()', data)
            self.assertIn('async', data)
            self.assertIn('/api/cart', data)
            self.assertIn('cartCount', data)

    def test_header_contains_dom_content_loaded_event(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for DOMContentLoaded event listener
            self.assertIn('DOMContentLoaded', data)
            self.assertIn('updateCartCount', data)

    def test_header_contains_cart_updated_event_listener(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for custom cartUpdated event listener
            self.assertIn('cartUpdated', data)

    def test_header_contains_styling(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for CSS styling blocks
            self.assertIn('#commonHeader', data)
            self.assertIn('.headerButton', data)
            self.assertIn('.cart-count', data)
            self.assertIn('.search-dropdown', data)

    def test_header_cart_button_conditional_rendering(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Unauthenticated user should not see cart button in header
            # (cart button is only rendered if session.get('authenticated') is true)
            self.assertNotIn('id="cartButton"', data)

    def test_header_contains_search_wrapper(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for search wrapper container
            self.assertIn('class="search-wrapper"', data)

    def test_header_contains_click_outside_close_dropdown(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for click-outside logic
            self.assertIn('document.addEventListener(\'click\'', data)
            self.assertIn('.closest(', data)
            self.assertIn('search-wrapper', data)

    def test_header_search_input_validation(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for search input validation (query.length < 2)
            self.assertIn('query.length < 2', data)
            self.assertIn('this.value.trim()', data)

    def test_header_contains_enter_key_handler(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for Enter key handling in search
            self.assertIn('e.key === \'Enter\'', data)

    def test_header_contains_max_results_limit(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for max 8 results limit
            self.assertIn('slice(0, 8)', data)

    def test_header_contains_seller_rating_display(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for seller rating in search results
            self.assertIn('product.seller.rating', data)
            self.assertIn('product.seller.name', data)
            self.assertIn('stars', data)


if __name__ == '__main__':
    unittest.main()
