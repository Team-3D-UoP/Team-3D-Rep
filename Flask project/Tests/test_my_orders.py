import os
import sys
import unittest

# Ensure project root is on sys.path so imports like `from app import app` work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class MyOrdersTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_my_orders_page_renders(self):
        rv = self.client.get('/my-orders')
        # page may redirect if the app enforces auth, accept 200 or 302
        self.assertIn(rv.status_code, (200, 302))
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('My Orders', data)
            self.assertIn("fetch('/api/orders/user-orders')", data)
            self.assertIn('id="deliveryOrders"', data)
            self.assertIn('id="collectionOrders"', data)
            self.assertIn('loadOrders();', data)
            self.assertIn('Loading orders...', data)

    def test_my_orders_template_contains_empty_state_text(self):
        rv = self.client.get('/my-orders')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # The template includes the "Please log in to view your orders" text inside the script
            self.assertIn('Please log in to view your orders', data)


if __name__ == '__main__':
    unittest.main()
