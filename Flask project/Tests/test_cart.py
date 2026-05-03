import os
import sys
import unittest

# Ensure project root is on sys.path so imports like `from app import app` work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class CartTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def authenticate(self):
        with self.client.session_transaction() as session:
            session['authenticated'] = True

    def test_cart_redirects_when_not_authenticated(self):
        rv = self.client.get('/cart')
        self.assertEqual(rv.status_code, 302)
        self.assertIn('/login', rv.headers.get('Location', ''))

    def test_cart_page_renders_when_authenticated(self):
        self.authenticate()
        rv = self.client.get('/cart')
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode('utf-8')
        self.assertIn('Shopping Cart', data)
        self.assertIn('Order Summary', data)
        self.assertIn('Proceed to Checkout', data)
        self.assertIn('Continue Shopping', data)

    def test_cart_contains_breadcrumb_and_container(self):
        self.authenticate()
        rv = self.client.get('/cart')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('cart-breadcrumb', data)
            self.assertIn('cart-container', data)
            self.assertIn('cart-content', data)
            self.assertIn('cart-items-section', data)
            self.assertIn('cart-summary', data)

    def test_cart_contains_loading_state(self):
        self.authenticate()
        rv = self.client.get('/cart')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('Loading your cart...', data)
            self.assertIn('spinner', data)
            self.assertIn('cartItemsContainer', data)

    def test_cart_contains_summary_fields(self):
        self.authenticate()
        rv = self.client.get('/cart')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('cartItemCount', data)
            self.assertIn('cartSubtotal', data)
            self.assertIn('cartShipping', data)
            self.assertIn('cartTotal', data)
            self.assertIn('Items:', data)
            self.assertIn('Subtotal:', data)
            self.assertIn('Shipping:', data)
            self.assertIn('Total:', data)

    def test_cart_contains_load_cart_function(self):
        self.authenticate()
        rv = self.client.get('/cart')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('async function loadCart()', data)
            self.assertIn("fetch('/api/cart')", data)
            self.assertIn('updateSummary(data)', data)

    def test_cart_contains_empty_cart_state(self):
        self.authenticate()
        rv = self.client.get('/cart')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('Your cart is empty', data)
            self.assertIn('Continue Shopping', data)

    def test_cart_contains_quantity_controls(self):
        self.authenticate()
        rv = self.client.get('/cart')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('function addOne(itemId)', data)
            self.assertIn('function removeOne(itemId)', data)
            self.assertIn('function updateQuantityFromCart(itemId, change)', data)
            self.assertIn('quantity-btn', data)
            self.assertIn('remove-btn', data)

    def test_cart_contains_remove_flow(self):
        self.authenticate()
        rv = self.client.get('/cart')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('function removeFromCart(itemId)', data)
            self.assertIn("/api/cart/remove", data)
            self.assertIn('confirm(', data)

    def test_cart_contains_checkout_flow(self):
        self.authenticate()
        rv = self.client.get('/cart')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('async function proceedToCheckout()', data)
            self.assertIn("/api/orders/place", data)
            self.assertIn('/api/cart/clear', data)
            self.assertIn('/my-orders', data)

    def test_cart_contains_escape_helper(self):
        self.authenticate()
        rv = self.client.get('/cart')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('function escapeHtml(text)', data)
            self.assertIn('&amp;', data)
            self.assertIn('&lt;', data)
            self.assertIn('&gt;', data)
            self.assertIn('&quot;', data)
            self.assertIn('&#039;', data)

    def test_cart_contains_cart_api_references(self):
        self.authenticate()
        rv = self.client.get('/cart')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('/api/cart/update', data)
            self.assertIn('/api/cart/remove', data)
            self.assertIn("document.dispatchEvent(new Event('cartUpdated'))", data)

    def test_cart_contains_styling(self):
        self.authenticate()
        rv = self.client.get('/cart')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('.cart-container', data)
            self.assertIn('.cart-summary', data)
            self.assertIn('.checkout-btn', data)
            self.assertIn('.continue-btn', data)
            self.assertIn('@media (max-width: 768px)', data)


if __name__ == '__main__':
    unittest.main()
