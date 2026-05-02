import os
import sys
import unittest

# Ensure project root is on sys.path so imports like `from app import app` work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class SellersPageTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_sellers_page_renders(self):
        rv = self.client.get('/sellers')
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode('utf-8')
        self.assertIn('Sellers - Team 3D', data)
        self.assertIn('Our Sellers', data)
        self.assertIn('Discover trusted sellers on Team 3D', data)

    def test_sellers_page_contains_grid_and_cards(self):
        rv = self.client.get('/sellers')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('class="sellers-grid"', data)
            self.assertIn('class="seller-card"', data)
            self.assertIn('class="seller-header"', data)
            self.assertIn('class="seller-body"', data)

    def test_sellers_page_renders_known_seller_data(self):
        rv = self.client.get('/sellers')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('Alex Mitchell', data)
            self.assertIn('3D Printing Expert', data)
            self.assertIn('4.9', data)
            self.assertIn('(287 reviews)', data)
            self.assertIn('Jan 15, 2022', data)
            self.assertIn('542', data)
            self.assertIn('2 hours', data)
            self.assertIn('98%', data)

    def test_sellers_page_renders_inactive_seller_badge(self):
        rv = self.client.get('/sellers')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('Fiona Walsh', data)
            self.assertIn('status-inactive', data)
            self.assertIn('Inactive', data)

    def test_sellers_page_contains_navigation_links(self):
        rv = self.client.get('/sellers')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('href="/seller/1"', data)
            self.assertIn('href="/seller/6"', data)
            self.assertIn('class="seller-card-link"', data)
            self.assertIn('View Profile', data)

    def test_sellers_page_contains_styling(self):
        rv = self.client.get('/sellers')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('linear-gradient(135deg', data)
            self.assertIn('.seller-card:hover', data)
            self.assertIn('.status-active', data)
            self.assertIn('.status-inactive', data)
            self.assertIn('.btn-view', data)


if __name__ == '__main__':
    unittest.main()
