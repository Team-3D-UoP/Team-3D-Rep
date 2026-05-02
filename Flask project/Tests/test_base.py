import os
import sys
import unittest

# Ensure project root is on sys.path so imports like `from app import app` work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class BaseTemplateTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_home_page_renders_base_shell(self):
        rv = self.client.get('/')
        self.assertEqual(rv.status_code, 200)
        html = rv.data.decode('utf-8')
        self.assertIn('<html lang="en">', html)
        self.assertIn('<main>', html)
        self.assertIn('</main>', html)
        self.assertIn('Home - Team 3D', html)

    def test_home_page_includes_header_and_footer(self):
        rv = self.client.get('/')
        self.assertEqual(rv.status_code, 200)
        html = rv.data.decode('utf-8')
        self.assertIn('id="commonHeader"', html)
        self.assertIn('id="commonFooter"', html)

    def test_home_page_has_shared_layout_styling(self):
        rv = self.client.get('/')
        self.assertEqual(rv.status_code, 200)
        html = rv.data.decode('utf-8')
        self.assertIn('max-width: 1200px', html)
        self.assertIn('min-height: 300px', html)
        self.assertIn('AutoPartFinder', html)


if __name__ == '__main__':
    unittest.main()
