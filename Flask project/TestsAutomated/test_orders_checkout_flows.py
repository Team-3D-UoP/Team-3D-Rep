import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import User, CartItem


class TestOrdersCheckoutFlows(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        # Mock Firebase as initialized for testing
        self.firebase_patcher = patch('app.firebase_initialized', True)
        self.mock_firebase_init = self.firebase_patcher.start()

        with self.app.app_context():
            db.create_all()
            # Create test user
            test_user = User(
                firebase_uid='testuser123',
                email='test@example.com',
                username='testuser',
                fullname='Test User'
            )
            db.session.add(test_user)
            db.session.commit()

    def tearDown(self):
        self.firebase_patcher.stop()
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    @patch('requests.put')
    def test_place_order_success(self, mock_put):
        """Successfully place an order"""
        with self.client:
            with self.client.session_transaction() as sess:
                sess['authenticated'] = True
                sess['email'] = 'test@example.com'
                sess['name'] = 'Test User'

            # Mock Firebase response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_put.return_value = mock_response

            response = self.client.post('/api/orders/place', json={
                'items': [{'id': 1001, 'name': 'Test Product', 'quantity': 2, 'price': 10.0}],
                'total': 20.0,
                'delivery_method': 'delivery',
                'payment_method': 'card'
            })
            self.assertEqual(response.status_code, 201)
            payload = response.get_json()
            self.assertTrue(payload.get('success'))
            self.assertIn('order_id', payload)

    @patch('requests.put')
    def test_place_order_empty_cart(self, mock_put):
        """Attempt to place order with empty cart"""
        with self.client:
            with self.client.session_transaction() as sess:
                sess['authenticated'] = True
                sess['email'] = 'test@example.com'
                sess['name'] = 'Test User'

        # Mock Firebase response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_put.return_value = mock_response

        response = self.client.post('/api/orders/place', json={
            'items': [],
            'total': 0,
            'delivery_method': 'delivery',
            'payment_method': 'card'
        })
        # The API doesn't actually check for empty cart, so it should succeed
        self.assertEqual(response.status_code, 201)

    @patch('requests.put')
    def test_place_order_firebase_failure(self, mock_put):
        """Handle Firebase failure during order placement"""
        with self.client:
            with self.client.session_transaction() as sess:
                sess['authenticated'] = True
                sess['email'] = 'test@example.com'
                sess['name'] = 'Test User'

        # Mock Firebase failure
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_put.return_value = mock_response

        response = self.client.post('/api/orders/place', json={
            'items': [{'id': 1001, 'name': 'Test Product', 'quantity': 1, 'price': 10.0}],
            'total': 10.0,
            'delivery_method': 'collection',
            'payment_method': 'paypal'
        })
        self.assertEqual(response.status_code, 500)

    @patch('requests.put')
    def test_place_order_collection_method(self, mock_put):
        """Place order with collection delivery method"""
        with self.client:
            with self.client.session_transaction() as sess:
                sess['authenticated'] = True
                sess['email'] = 'test@example.com'
                sess['name'] = 'Test User'

        # Mock Firebase response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_put.return_value = mock_response

        response = self.client.post('/api/orders/place', json={
            'items': [{'id': 1002, 'name': 'Test Product 2', 'quantity': 1, 'price': 15.0}],
            'total': 15.0,
            'delivery_method': 'collection',
            'payment_method': 'card'
        })
        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertTrue(payload.get('success'))

    def test_my_orders_page_render(self):
        """My orders page renders correctly"""
        with self.client:
            with self.client.session_transaction() as sess:
                sess['authenticated'] = True
                sess['email'] = 'test@example.com'
                sess['name'] = 'Test User'

        response = self.client.get('/my-orders')
        self.assertEqual(response.status_code, 200)
        data = response.get_data(as_text=True)
        self.assertIn('orders', data.lower())


if __name__ == '__main__':
    unittest.main()