import unittest
import sys
import os
from pathlib import Path

# Add parent directory to path to import app and models
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask
from app import app, db
from models import User
import json
from unittest.mock import patch, MagicMock


class TestCompatibilityCheckingFlows(unittest.TestCase):
    """Test suite for vehicle compatibility checking functionality"""

    def setUp(self):
        """Set up test client and database before each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            # Create test user
            test_user = User(
                firebase_uid='test_firebase_uid',
                username='testuser',
                email='test@example.com',
                fullname='Test User'
            )
            db.session.add(test_user)
            db.session.commit()

    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_compatibility_check_valid_inputs(self):
        """Test compatibility checking with valid vehicle and part inputs"""
        with self.client:
            # Test basic compatibility check
            response = self.client.post('/compatibility/check', json={
                'vehicle_id': 1,
                'part_id': 1
            })
            # Should handle request gracefully
            self.assertNotEqual(response.status_code, 500)

    def test_compatibility_check_invalid_vehicle_id(self):
        """Test compatibility checking with invalid vehicle ID"""
        with self.client:
            response = self.client.post('/compatibility/check', json={
                'vehicle_id': 999999,
                'part_id': 1
            })
            # Should handle gracefully
            self.assertNotEqual(response.status_code, 500)

    def test_compatibility_check_invalid_part_id(self):
        """Test compatibility checking with invalid part ID"""
        with self.client:
            response = self.client.post('/compatibility/check', json={
                'vehicle_id': 1,
                'part_id': 999999
            })
            # Should handle gracefully
            self.assertNotEqual(response.status_code, 500)

    def test_compatibility_check_missing_fields(self):
        """Test compatibility checking with missing required fields"""
        with self.client:
            # Missing part_id
            response = self.client.post('/compatibility/check', json={
                'vehicle_id': 1
            })
            # Should handle gracefully
            self.assertNotEqual(response.status_code, 500)
            
            # Missing vehicle_id
            response = self.client.post('/compatibility/check', json={
                'part_id': 1
            })
            # Should handle gracefully
            self.assertNotEqual(response.status_code, 500)

    def test_get_compatible_parts(self):
        """Test retrieving compatible parts for a vehicle"""
        with self.client:
            response = self.client.get('/vehicle/1/compatible-parts')
            # Should handle request gracefully
            self.assertIn(response.status_code, [200, 302, 404])
            self.assertNotEqual(response.status_code, 500)

    def test_get_compatible_parts_invalid_id(self):
        """Test retrieving compatible parts with invalid vehicle ID"""
        with self.client:
            response = self.client.get('/vehicle/999999/compatible-parts')
            # Should handle gracefully
            self.assertNotEqual(response.status_code, 500)

    def test_compatibility_check_negative_ids(self):
        """Test compatibility checking with negative IDs"""
        with self.client:
            response = self.client.post('/compatibility/check', json={
                'vehicle_id': -1,
                'part_id': -1
            })
            # Should handle gracefully
            self.assertNotEqual(response.status_code, 500)

    def test_compatibility_check_zero_ids(self):
        """Test compatibility checking with zero IDs"""
        with self.client:
            response = self.client.post('/compatibility/check', json={
                'vehicle_id': 0,
                'part_id': 0
            })
            # Should handle gracefully
            self.assertNotEqual(response.status_code, 500)

    def test_compatibility_check_non_numeric_ids(self):
        """Test compatibility checking with non-numeric IDs"""
        with self.client:
            response = self.client.post('/compatibility/check', json={
                'vehicle_id': 'abc',
                'part_id': 'xyz'
            })
            # Should handle gracefully
            self.assertNotEqual(response.status_code, 500)


if __name__ == '__main__':
    unittest.main()
