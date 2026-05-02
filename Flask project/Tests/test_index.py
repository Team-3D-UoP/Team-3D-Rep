import os
import sys
import unittest

# Ensure project root is on sys.path so imports like `from app import app` work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class IndexTaxCalculatorTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_index_page_renders(self):
        rv = self.client.get('/')
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode('utf-8')
        self.assertIn('Tax Calculator', data)

    def test_index_contains_form_structure(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for form with id and method
            self.assertIn('id="tax-form"', data)
            self.assertIn('<form', data)

    def test_index_contains_employment_income_input(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for employment income input field
            self.assertIn('id="input-empl"', data)
            self.assertIn('Employment income', data)
            self.assertIn('type="number"', data)
            self.assertIn('step="any"', data)

    def test_index_contains_savings_income_input(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for savings income input field
            self.assertIn('id="input-savings"', data)
            self.assertIn('Savings income', data)
            self.assertIn('type="number"', data)

    def test_index_contains_feedback_containers(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for feedback div containers
            self.assertIn('id="feedbackempl"', data)
            self.assertIn('id="feedbacksavings"', data)

    def test_index_contains_calculate_button(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for calculate button
            self.assertIn('onclick="calculate()"', data)
            self.assertIn('Preview', data)
            self.assertIn('type="button"', data)

    def test_index_contains_calculate_function(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for calculate function
            self.assertIn('function calculate()', data)
            self.assertIn('document.getElementById(\'input-empl\')', data)
            self.assertIn('document.getElementById(\'input-savings\')', data)
            self.assertIn('axios.post("/api/calcTax"', data)

    def test_index_contains_save_function(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for save function
            self.assertIn('function save()', data)
            self.assertIn('axios.post("/api/saveTax"', data)
            self.assertIn('Saved successfully', data)

    def test_index_contains_display_error_function(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for error handling function
            self.assertIn('function displayError(err)', data)
            self.assertIn('Please provide your income', data)
            self.assertIn('Please provide positive income', data)

    def test_index_contains_error_messages(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for all error messages
            self.assertIn('Please provide your income', data)
            self.assertIn('Please provide positive income', data)
            self.assertIn('Both incomes must be numerical', data)
            self.assertIn('Error saving data', data)

    def test_index_contains_axios_cdn(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for Axios library
            self.assertIn('axios', data)
            self.assertIn('cdn.jsdelivr.net', data)

    def test_index_contains_confirm_redirect(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for redirect to confirm page
            self.assertIn('window.location.href = "/confirm"', data)

    def test_index_contains_feedback_clear_on_submit(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for feedback clearing logic
            self.assertIn('feedback1.textContent = feedback2.textContent = ""', data)

    def test_index_contains_result_class_styling(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for result class application
            self.assertIn('feedback1.className = feedback2.className = "result"', data)
            self.assertIn('.result', data)

    def test_index_contains_error_class_styling(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for error class
            self.assertIn('.error', data)

    def test_index_form_inputs_are_required(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for required attribute on inputs
            self.assertIn('required', data)

    def test_index_contains_variable_initialization(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for variable initialization
            self.assertIn('let feedback1 = document.getElementById("feedbackempl")', data)
            self.assertIn('let feedback2= document.getElementById("feedbacksavings")', data)

    def test_index_contains_error_checking_logic(self):
        rv = self.client.get('/')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            # Check for error response checking
            self.assertIn('err.response.data.error1', data)
            self.assertIn('err.response.data.error2', data)
            self.assertIn('err.response.error4', data)


if __name__ == '__main__':
    unittest.main()
