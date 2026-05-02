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

    def test_my_orders_contains_tab_switching_function(self):
        rv = self.client.get('/my-orders')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for tab switching function and tab buttons
            self.assertIn('function switchTab(event, tabName)', data)
            self.assertIn('onclick="switchTab(event, \'delivery\')"', data)
            self.assertIn('onclick="switchTab(event, \'collection\')"', data)
            self.assertIn('.tab-button.active', data)
            self.assertIn('tab-content', data)

    def test_my_orders_contains_load_orders_function(self):
        rv = self.client.get('/my-orders')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for async loadOrders function
            self.assertIn('async function loadOrders()', data)
            self.assertIn('function renderOrders(containerId, orders)', data)
            self.assertIn('data.orders || []', data)
            self.assertIn('delivery_method', data)

    def test_my_orders_contains_navigation_elements(self):
        rv = self.client.get('/my-orders')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check breadcrumb navigation
            self.assertIn('<a href="/">Home</a>', data)
            self.assertIn('<a href="/account">My Account</a>', data)
            self.assertIn('<strong>My Orders</strong>', data)
            # Check back link
            self.assertIn('← Back to My Account', data)
            self.assertIn('href="/account"', data)

    def test_my_orders_contains_sidebar_navigation(self):
        rv = self.client.get('/my-orders')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check sidebar navigation items
            self.assertIn('Account Overview', data)
            self.assertIn('My Orders', data)
            self.assertIn('Personal Details', data)
            self.assertIn('My Wish List', data)
            # Check sidebar active state
            self.assertIn('nav-item active', data)
            self.assertIn('href="/account"', data)
            self.assertIn('href="/my-orders"', data)
            self.assertIn('href="/personal-details"', data)

    def test_my_orders_contains_table_structure(self):
        rv = self.client.get('/my-orders')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check table headers and structure
            self.assertIn('class="table-header"', data)
            self.assertIn('class="table-row"', data)
            self.assertIn('class="table-cell"', data)
            self.assertIn('Order ID', data)
            self.assertIn('Date', data)
            self.assertIn('Total', data)
            self.assertIn('Status', data)

    def test_my_orders_contains_status_badges(self):
        rv = self.client.get('/my-orders')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check status badge CSS classes
            self.assertIn('status-processing', data)
            self.assertIn('status-delivered', data)
            self.assertIn('status-cancelled', data)
            self.assertIn('class="status-badge', data)

    def test_my_orders_contains_tab_content_areas(self):
        rv = self.client.get('/my-orders')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for both tab content containers
            self.assertIn('id="delivery"', data)
            self.assertIn('id="collection"', data)
            self.assertIn('id="deliveryOrders"', data)
            self.assertIn('id="collectionOrders"', data)
            self.assertIn('class="tab-content active"', data)

    def test_my_orders_contains_error_handling(self):
        rv = self.client.get('/my-orders')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for error handling in loadOrders
            self.assertIn('catch (error)', data)
            self.assertIn('console.error(\'Error loading orders:\'', data)
            self.assertIn('Error loading orders. Please try again.', data)

    def test_my_orders_contains_order_filtering_logic(self):
        rv = self.client.get('/my-orders')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for order filtering by delivery method
            self.assertIn('o.delivery_method === \'delivery\'', data)
            self.assertIn('o.delivery_method === \'collection\'', data)
            self.assertIn('filter(o =>', data)

    def test_my_orders_contains_date_formatting(self):
        rv = self.client.get('/my-orders')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for date formatting logic
            self.assertIn('toLocaleDateString', data)
            self.assertIn('en-GB', data)
            self.assertIn('order.created_at', data)

    def test_my_orders_contains_currency_formatting(self):
        rv = self.client.get('/my-orders')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for currency formatting
            self.assertIn('parseFloat(order.total).toFixed(2)', data)
            self.assertIn('£', data)


if __name__ == '__main__':
    unittest.main()
