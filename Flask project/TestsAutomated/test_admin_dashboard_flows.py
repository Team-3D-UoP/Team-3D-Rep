"""
Automated tests for Admin Dashboard flows
This file will cover admin login plus admin dashboard API behavior
from the test plan.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestAdminDashboardFlows(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    # TODO: Add admin dashboard flow tests here


if __name__ == '__main__':
    unittest.main()
