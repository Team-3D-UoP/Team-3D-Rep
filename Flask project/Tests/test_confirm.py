import os
import sys
import unittest

# Ensure project root is on sys.path so imports like `from app import app` work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class ConfirmTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_confirm_page_renders_with_session_values(self):
        with self.client.session_transaction() as session:
            session['empl'] = 50000
            session['savings'] = 1000

        rv = self.client.get('/confirm')
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode('utf-8')
        self.assertIn('Tax Calculator', data)
        self.assertIn('Incomes inputted', data)
        self.assertIn('50000', data)
        self.assertIn('1000', data)

    def test_confirm_contains_save_button(self):
        with self.client.session_transaction() as session:
            session['empl'] = 50000
            session['savings'] = 1000

        rv = self.client.get('/confirm')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('onclick="save()"', data)
            self.assertIn('Save', data)
            self.assertIn('function save()', data)
            self.assertIn('axios.post("/api/saveTax"', data)

    def test_confirm_contains_feedback_containers(self):
        with self.client.session_transaction() as session:
            session['empl'] = 50000
            session['savings'] = 1000

        rv = self.client.get('/confirm')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('id="feedbacksaved"', data)
            self.assertIn('id="tax-emp"', data)
            self.assertIn('id="tax-saving"', data)

    def test_confirm_contains_result_and_error_styles(self):
        with self.client.session_transaction() as session:
            session['empl'] = 50000
            session['savings'] = 1000

        rv = self.client.get('/confirm')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('.result', data)
            self.assertIn('.error', data)
            self.assertIn('feedback1.className = "result"', data)
            self.assertIn('feedback1.className = "error"', data)

    def test_confirm_contains_tax_output_text(self):
        with self.client.session_transaction() as session:
            session['empl'] = 50000
            session['savings'] = 1000

        rv = self.client.get('/confirm')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('Tax on income:', data)
            self.assertIn('Tax on savings:', data)
            self.assertIn('feedback2.textContent', data)
            self.assertIn('feedback3.textContent', data)

    def test_confirm_contains_display_error_function(self):
        with self.client.session_transaction() as session:
            session['empl'] = 50000
            session['savings'] = 1000

        rv = self.client.get('/confirm')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('function displayError(err)', data)
            self.assertIn('Please provide your income', data)
            self.assertIn('Please provide positive income', data)
            self.assertIn('Both incomes must be numerical', data)
            self.assertIn('Error saving data', data)

    def test_confirm_contains_axios_cdn(self):
        with self.client.session_transaction() as session:
            session['empl'] = 50000
            session['savings'] = 1000

        rv = self.client.get('/confirm')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('axios', data)
            self.assertIn('cdn.jsdelivr.net', data)

    def test_confirm_contains_session_value_bindings(self):
        with self.client.session_transaction() as session:
            session['empl'] = 12345
            session['savings'] = 678

        rv = self.client.get('/confirm')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('12345', data)
            self.assertIn('678', data)


if __name__ == '__main__':
    unittest.main()
