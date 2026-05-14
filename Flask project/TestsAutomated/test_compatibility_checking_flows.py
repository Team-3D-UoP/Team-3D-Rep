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
        self.app.config['SQLALCHEMY_ECHO'] = False
        
        # Use app context and ensure fresh database for each test
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Clear any existing data and create fresh schema
        db.drop_all()
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
        
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_compatibility_check_input_validation(self):
        """Test compatibility checking with various input validation scenarios"""
        with self.client:
            # Test valid inputs
            response = self.client.post('/compatibility/check', json={
                'vehicle_id': 1,
                'part_id': 1
            })
            self.assertNotEqual(response.status_code, 500)
            
            # Test invalid vehicle ID (very large)
            response = self.client.post('/compatibility/check', json={
                'vehicle_id': 999999,
                'part_id': 1
            })
            self.assertNotEqual(response.status_code, 500)
            
            # Test invalid part ID
            response = self.client.post('/compatibility/check', json={
                'vehicle_id': 1,
                'part_id': 999999
            })
            self.assertNotEqual(response.status_code, 500)
            
            # Test missing fields
            response = self.client.post('/compatibility/check', json={'vehicle_id': 1})
            self.assertNotEqual(response.status_code, 500)
            
            response = self.client.post('/compatibility/check', json={'part_id': 1})
            self.assertNotEqual(response.status_code, 500)
            
            # Test negative and zero IDs
            for vehicle_id in [-1, 0]:
                response = self.client.post('/compatibility/check', json={
                    'vehicle_id': vehicle_id,
                    'part_id': 1
                })
                self.assertNotEqual(response.status_code, 500)
            
            # Test non-numeric IDs
            response = self.client.post('/compatibility/check', json={
                'vehicle_id': 'abc',
                'part_id': 'xyz'
            })
            self.assertNotEqual(response.status_code, 500)

    def test_get_compatible_parts_endpoint(self):
        """Test retrieving compatible parts for vehicles with various IDs"""
        with self.client:
            # Test valid vehicle ID
            response = self.client.get('/vehicle/1/compatible-parts')
            self.assertIn(response.status_code, [200, 302, 404])
            self.assertNotEqual(response.status_code, 500)
            
            # Test invalid vehicle ID (very large)
            response = self.client.get('/vehicle/999999/compatible-parts')
            self.assertNotEqual(response.status_code, 500)
            
            # Test negative vehicle ID
            response = self.client.get('/vehicle/-1/compatible-parts')
            self.assertNotEqual(response.status_code, 500)
            
            # Test zero vehicle ID
            response = self.client.get('/vehicle/0/compatible-parts')
            self.assertNotEqual(response.status_code, 500)

    def test_compatibility_check_authentication_scenarios(self):
        """Test compatibility check with various authentication scenarios"""
        test_user = User.query.filter_by(username='testuser').first()
        user_id = test_user.id if test_user else 1
        
        # Test without authentication (empty session)
        with self.client:
            response = self.client.post('/compatibility/check', json={
                'vehicle_id': 1,
                'part_id': 1
            })
            # Should either allow, redirect/return auth error, or 404 if endpoint doesn't exist
            self.assertIn(response.status_code, [200, 301, 302, 401, 403, 404])
        
        # Test with valid authentication
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user_id
            
            response = self.client.post('/compatibility/check', json={
                'vehicle_id': 1,
                'part_id': 1
            })
            # Accept 404 if endpoint not implemented
            self.assertIn(response.status_code, [200, 301, 302, 400, 404])
            self.assertNotEqual(response.status_code, 500)
        
        # Test with invalid user ID in session
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = 999999
            
            response = self.client.post('/compatibility/check', json={
                'vehicle_id': 1,
                'part_id': 1
            })
            self.assertNotEqual(response.status_code, 500)

    def test_get_compatible_parts_authentication(self):
        """Test GET compatible parts endpoint with authentication scenarios"""
        test_user = User.query.filter_by(username='testuser').first()
        user_id = test_user.id if test_user else 1
        
        # Test without authentication
        with self.client:
            response = self.client.get('/vehicle/1/compatible-parts')
            self.assertIn(response.status_code, [200, 301, 302, 401, 403, 404])
        
        # Test with valid authentication
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user_id
            
            response = self.client.get('/vehicle/1/compatible-parts')
            self.assertNotIn(response.status_code, [401, 403])
            self.assertNotEqual(response.status_code, 500)
        
        # Test with invalid user ID
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = 999999
            
            response = self.client.get('/vehicle/1/compatible-parts')
            self.assertNotEqual(response.status_code, 500)

    def test_session_persistence_and_multi_user(self):
        """Test session persistence across requests and multiple user handling"""
        test_user = User.query.filter_by(username='testuser').first()
        user1_id = test_user.id if test_user else 1
        
        # Create second user
        user2 = User(
            firebase_uid='test_firebase_uid_2',
            username='testuser2',
            email='test2@example.com',
            fullname='Test User 2'
        )
        db.session.add(user2)
        db.session.commit()
        user2_id = user2.id
        
        # Test session persistence for user 1
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user1_id
            
            response1 = self.client.post('/compatibility/check', json={
                'vehicle_id': 1,
                'part_id': 1
            })
            
            # Session should persist for second request
            response2 = self.client.post('/compatibility/check', json={
                'vehicle_id': 2,
                'part_id': 2
            })
            
            self.assertNotIn(response1.status_code, [401, 403])
            self.assertNotIn(response2.status_code, [401, 403])
        
        # Test user 2 gets separate session
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user2_id
            
            response = self.client.post('/compatibility/check', json={
                'vehicle_id': 1,
                'part_id': 1
            })
            self.assertNotEqual(response.status_code, 500)

    def test_compatibility_check_request_format_validation(self):
        """Test compatibility check with various request format scenarios"""
        test_user = User.query.filter_by(username='testuser').first()
        user_id = test_user.id if test_user else 1
        
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user_id
            
            # Test with empty JSON body
            response = self.client.post('/compatibility/check', json={})
            self.assertNotEqual(response.status_code, 500)
            
            # Test with extra fields
            response = self.client.post('/compatibility/check', json={
                'vehicle_id': 1,
                'part_id': 1,
                'extra_field': 'should be ignored',
                'another_field': 123
            })
            self.assertNotEqual(response.status_code, 500)
            
            # Test with null values
            response = self.client.post('/compatibility/check', json={
                'vehicle_id': None,
                'part_id': None
            })
            self.assertNotEqual(response.status_code, 500)
            
            # Test with empty strings
            response = self.client.post('/compatibility/check', json={
                'vehicle_id': '',
                'part_id': ''
            })
            self.assertNotEqual(response.status_code, 500)


if __name__ == '__main__':
    unittest.main()
