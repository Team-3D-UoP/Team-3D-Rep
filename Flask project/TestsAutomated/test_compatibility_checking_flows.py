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

    # ===== Authentication & Authorization Tests =====

    def test_compatibility_check_without_authentication(self):
        """Test compatibility check without user authentication"""
        with self.client:
            # Make request without any session/auth
            response = self.client.post('/compatibility/check', json={
                'vehicle_id': 1,
                'part_id': 1
            })
            # Should either allow access or redirect/return auth error
            # Common responses: 401 (unauthorized), 302 (redirect to login), 200 (public endpoint)
            self.assertIn(response.status_code, [200, 301, 302, 401, 403])

    def test_compatibility_check_with_valid_authentication(self):
        """Test compatibility check with valid user authentication"""
        with self.app.app_context():
            test_user = User.query.filter_by(username='testuser').first()
            user_id = test_user.id if test_user else 1
        
        with self.client:
            # Set valid session
            with self.client.session_transaction() as sess:
                sess['user_id'] = user_id
            
            response = self.client.post('/compatibility/check', json={
                'vehicle_id': 1,
                'part_id': 1
            })
            # Should not return auth errors
            self.assertNotIn(response.status_code, [401, 403])
            self.assertNotEqual(response.status_code, 500)

    def test_compatibility_check_with_invalid_user_id(self):
        """Test compatibility check with invalid user ID in session"""
        with self.client:
            # Set invalid user ID in session
            with self.client.session_transaction() as sess:
                sess['user_id'] = 999999
            
            response = self.client.post('/compatibility/check', json={
                'vehicle_id': 1,
                'part_id': 1
            })
            # Should handle gracefully - either reject auth or continue
            self.assertNotEqual(response.status_code, 500)

    def test_get_compatible_parts_without_authentication(self):
        """Test retrieving compatible parts without user authentication"""
        with self.client:
            response = self.client.get('/vehicle/1/compatible-parts')
            # Should either allow access or redirect/return auth error
            self.assertIn(response.status_code, [200, 301, 302, 401, 403, 404])

    def test_get_compatible_parts_with_valid_authentication(self):
        """Test retrieving compatible parts with valid user authentication"""
        with self.app.app_context():
            test_user = User.query.filter_by(username='testuser').first()
            user_id = test_user.id if test_user else 1
        
        with self.client:
            # Set valid session
            with self.client.session_transaction() as sess:
                sess['user_id'] = user_id
            
            response = self.client.get('/vehicle/1/compatible-parts')
            # Should not return auth errors
            self.assertNotIn(response.status_code, [401, 403])
            self.assertNotEqual(response.status_code, 500)

    def test_get_compatible_parts_with_invalid_user_id(self):
        """Test retrieving compatible parts with invalid user ID in session"""
        with self.client:
            # Set invalid user ID in session
            with self.client.session_transaction() as sess:
                sess['user_id'] = 999999
            
            response = self.client.get('/vehicle/1/compatible-parts')
            # Should handle gracefully
            self.assertNotEqual(response.status_code, 500)

    def test_compatibility_check_session_empty(self):
        """Test compatibility check with empty session data"""
        with self.client:
            # Explicitly set empty session
            with self.client.session_transaction() as sess:
                pass  # Session remains empty
            
            response = self.client.post('/compatibility/check', json={
                'vehicle_id': 1,
                'part_id': 1
            })
            # Should handle gracefully
            self.assertNotEqual(response.status_code, 500)

    def test_compatibility_check_with_different_users(self):
        """Test that different users' sessions are handled separately"""
        with self.app.app_context():
            # Create a second test user
            test_user = User.query.filter_by(username='testuser').first()
            user1_id = test_user.id if test_user else 1
            
            user2 = User(
                firebase_uid='test_firebase_uid_2',
                username='testuser2',
                email='test2@example.com',
                fullname='Test User 2'
            )
            db.session.add(user2)
            db.session.commit()
            user2_id = user2.id
        
        # First user's request
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user1_id
            
            response1 = self.client.post('/compatibility/check', json={
                'vehicle_id': 1,
                'part_id': 1
            })
            self.assertNotEqual(response1.status_code, 500)
        
        # Second user's request
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = user2_id
            
            response2 = self.client.post('/compatibility/check', json={
                'vehicle_id': 1,
                'part_id': 1
            })
            self.assertNotEqual(response2.status_code, 500)

    def test_compatibility_check_session_persistence(self):
        """Test that session persists across multiple requests"""
        with self.app.app_context():
            test_user = User.query.filter_by(username='testuser').first()
            user_id = test_user.id if test_user else 1
        
        with self.client:
            # Set session once
            with self.client.session_transaction() as sess:
                sess['user_id'] = user_id
            
            # First request
            response1 = self.client.post('/compatibility/check', json={
                'vehicle_id': 1,
                'part_id': 1
            })
            
            # Second request - session should persist
            response2 = self.client.post('/compatibility/check', json={
                'vehicle_id': 2,
                'part_id': 2
            })
            
            # Both should succeed without auth errors
            self.assertNotIn(response1.status_code, [401, 403])
            self.assertNotIn(response2.status_code, [401, 403])


if __name__ == '__main__':
    unittest.main()
