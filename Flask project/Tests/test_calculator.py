import os
import sys
import unittest

# Ensure project root is on sys.path so imports like `from app import app` work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from flask import render_template


class CalculatorTemplateTests(unittest.TestCase):
    def test_calculator_template_renders(self):
        with app.app_context():
            html = render_template('calculator.html')

        self.assertIn('Tax Calculator', html)
        self.assertIn('Tax to pay', html)

    def test_calculator_template_contains_basic_structure(self):
        with app.app_context():
            html = render_template('calculator.html')

        self.assertIn('<html>', html)
        self.assertIn('<head>', html)
        self.assertIn('<body>', html)
        self.assertIn('<h1>Tax to pay</h1>', html)

    def test_calculator_template_is_minimal(self):
        with app.app_context():
            html = render_template('calculator.html')

        self.assertNotIn('axios', html)
        self.assertNotIn('script', html.lower())


if __name__ == '__main__':
    unittest.main()
