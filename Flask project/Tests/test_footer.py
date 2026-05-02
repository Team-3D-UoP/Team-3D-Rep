import os
import sys
import unittest

# Ensure project root is on sys.path so imports like `from app import app` work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class FooterTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_footer_renders_on_home_page(self):
        rv = self.client.get('/')
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode('utf-8')
        # Footer should be included via base.html
        self.assertIn('id="commonFooter"', data)

    def test_footer_contains_return_to_home_section(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for Return to home section
            self.assertIn('Return to home', data)
            self.assertIn('Main home page', data)

    def test_footer_contains_home_link(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for home link with url_for('home') reference
            self.assertIn('<a href="/">', data)

    def test_footer_contains_shop_with_us_section(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for Shop with us section
            self.assertIn('Shop with us', data)
            self.assertIn('Go to our', data)
            self.assertIn('search page', data)
            self.assertIn('find what you need', data)

    def test_footer_contains_contact_us_section(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for Contact us section
            self.assertIn('Contact us', data)
            self.assertIn('Github', data)

    def test_footer_contains_github_link(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for GitHub link
            self.assertIn('https://github.com/Team-3D-UoP/Team-3D-Rep', data)

    def test_footer_contains_about_us_section(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for About us section
            self.assertIn('About us', data)

    def test_footer_contains_app_description(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for app description
            self.assertIn('AutoPartFinder', data)
            self.assertIn('buy car parts online', data)
            self.assertIn('registering their components', data)
            self.assertIn('requesting help from professionals', data)

    def test_footer_contains_section_headings(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for all h3 headings
            self.assertIn('<h3>', data)

    def test_footer_contains_styling(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for CSS styling blocks
            self.assertIn('#commonFooter', data)
            self.assertIn('background-color: #003d7a', data)

    def test_footer_link_styling(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for link styling
            self.assertIn('#commonFooter a', data)
            self.assertIn('color: #7fb3ff', data)

    def test_footer_link_hover_effect(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for hover effect on links
            self.assertIn(':hover', data)
            self.assertIn('text-decoration: underline', data)

    def test_footer_contains_paragraphs(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for paragraph tags
            self.assertIn('<p>', data)

    def test_footer_border_styling(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for border-top styling
            self.assertIn('border-top: 2px solid #002d5a', data)

    def test_footer_padding_styling(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for padding styling
            self.assertIn('padding: 2rem', data)

    def test_footer_margin_top_styling(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for margin-top styling
            self.assertIn('margin-top: 3rem', data)

    def test_footer_text_color(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for text color
            self.assertIn('color: white', data)
            self.assertIn('color: #e0e0e0', data)

    def test_footer_max_width_constraint(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for max-width constraint
            self.assertIn('max-width: 1200px', data)

    def test_footer_heading_styling(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for h3 styling
            self.assertIn('#commonFooter h3', data)
            self.assertIn('font-weight: bold', data)

    def test_footer_first_heading_no_top_margin(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for first-child selector
            self.assertIn(':first-child', data)
            self.assertIn('margin-top: 0', data)

    def test_footer_links_no_underline_default(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for text-decoration: none on links
            self.assertIn('text-decoration: none', data)

    def test_footer_links_font_weight(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for link font-weight
            self.assertIn('font-weight: 500', data)

    def test_footer_line_height(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for line-height styling
            self.assertIn('line-height: 1.5', data)

    def test_footer_font_size(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for font-size styling
            self.assertIn('font-size: 0.95rem', data)
            self.assertIn('font-size: 1rem', data)

    def test_footer_transition_effect(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for transition effect
            self.assertIn('transition: color 0.3s ease', data)


if __name__ == '__main__':
    unittest.main()
