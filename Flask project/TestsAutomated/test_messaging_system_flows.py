"""
Automated tests for Messaging System flows
Tests all partitions from the test plan:
- Open the support chat (chat bubble)
- Send valid messages
- Empty message (error handling)
- Long message (edge case)
- Close chat window
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import User, ChatMessage


class TestMessagingSystemFlows(unittest.TestCase):
    """Test suite for messaging system workflows based on test plan"""

    def setUp(self):
        """Set up test client and database before each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        # Mock Firebase as initialized for testing
        self.firebase_patcher = patch('app.firebase_initialized', True)
        self.mock_firebase_init = self.firebase_patcher.start()
        
        with self.app.app_context():
            db.create_all()
            # Create test user
            test_user = User(
                firebase_uid='chat_test_user',
                email='chatuser@gmail.com',
                username='chatuser',
                fullname='Chat Test User'
            )
            db.session.add(test_user)
            db.session.commit()
            self.test_user_id = test_user.id
            self.test_email = 'chatuser@gmail.com'
            self.test_name = 'Chat Test User'

    def tearDown(self):
        """Clean up after each test"""
        self.firebase_patcher.stop()
        
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # ========================
    # TEST PLAN PARTITION: Open the Support Chat
    # ========================
    def test_open_support_chat_bubble(self):
        """
        Partition: Open the support chat
        Input: User clicks support chat bubble
        Expected output: Chat pop-up window opens
        Valid: ✓
        
        Note: Chat is accessed via API endpoints, not a page route.
        This tests that the chat API is accessible (prerequisite for chat to open).
        """
        # Test that chat send endpoint is accessible
        message_data = {
            'message': 'Testing chat access',
            'email': self.test_email,
            'name': self.test_name
        }
        
        response = self.client.post(
            '/api/chat/send',
            data=json.dumps(message_data),
            content_type='application/json'
        )
        
        # Should return 201 (created) - chat endpoint exists and is accessible
        self.assertIn(response.status_code, [200, 201])

    # ========================
    # TEST PLAN PARTITION: Send Valid Messages
    # ========================
    def test_send_valid_message(self):
        """
        Partition: Send valid messages
        Input: User enters a valid message and clicks send
        Expected output: Message is displayed in chat and sent to backend
        Valid: ✓
        """
        
        # Send a valid message
        message_data = {
            'message': 'Hello, I need help with my car parts order',
            'email': self.test_email,
            'name': self.test_name
        }
        
        response = self.client.post(
            '/api/chat/send',
            data=json.dumps(message_data),
            content_type='application/json'
        )
        
        # Should be accepted (201 or 200)
        self.assertIn(response.status_code, [200, 201])
        response_data = json.loads(response.data)
        self.assertTrue(response_data.get('success'))

    # ========================
    # TEST PLAN PARTITION: Empty Message
    # ========================
    def test_send_empty_message(self):
        """
        Partition: Empty message
        Input: User leaves message box empty and clicks send
        Expected output: Message is not sent or error message is shown
        Valid: i (Invalid)
        """
        # Send an empty message
        message_data = {
            'message': '',  # Empty!
            'email': self.test_email,
            'name': self.test_name
        }
        
        response = self.client.post(
            '/api/chat/send',
            data=json.dumps(message_data),
            content_type='application/json'
        )
        
        # Should fail - empty message
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)

    # ========================
    # TEST PLAN PARTITION: Long Message
    # ========================
    def test_send_long_message(self):
        """
        Partition: Long message
        Input: User enters a long message and clicks send
        Expected output: Message is submitted and appears in chat safely without crashes
        Valid: ✓
        """
        
        # Send a very long message (testing edge case)
        long_text = 'A' * 2000  # 2000 character message
        message_data = {
            'message': long_text,
            'email': self.test_email,
            'name': self.test_name
        }
        
        response = self.client.post(
            '/api/chat/send',
            data=json.dumps(message_data),
            content_type='application/json'
        )
        
        # Should handle long messages gracefully
        self.assertIn(response.status_code, [200, 201])
        response_data = json.loads(response.data)
        self.assertTrue(response_data.get('success'))

    # ========================
    # TEST PLAN PARTITION: Close Chat Window
    # ========================
    def test_close_chat_window(self):
        """
        Partition: Close chat window
        Input: User clicks the X close button
        Expected output: Chat pop-up closes
        Valid: ✓
        
        Note: Chat window opening/closing is client-side functionality.
        We test that chat can be accessed and then reopened (simulating close/reopen).
        """
        # Send a message (simulates opening chat and sending)
        message_data_1 = {
            'message': 'First message',
            'email': self.test_email,
            'name': self.test_name
        }
        response_1 = self.client.post(
            '/api/chat/send',
            data=json.dumps(message_data_1),
            content_type='application/json'
        )
        self.assertIn(response_1.status_code, [200, 201])
        
        # Chat "closes" and is reopened - user sends another message
        message_data_2 = {
            'message': 'Second message after reopening',
            'email': self.test_email,
            'name': self.test_name
        }
        response_2 = self.client.post(
            '/api/chat/send',
            data=json.dumps(message_data_2),
            content_type='application/json'
        )
        
        # Should still work after "reopening"
        self.assertIn(response_2.status_code, [200, 201])

    # ========================
    # ADDITIONAL: Message with special characters
    # ========================
    def test_send_message_with_special_characters(self):
        """Test that messages with special characters are handled safely"""
        
        # Message with special characters
        message_data = {
            'message': 'Hello! @#$%^&*()_+ <script>alert("xss")</script>',
            'email': self.test_email,
            'name': self.test_name
        }
        
        response = self.client.post(
            '/api/chat/send',
            data=json.dumps(message_data),
            content_type='application/json'
        )
        
        # Should accept special characters (proper escaping happens on frontend/backend)
        self.assertIn(response.status_code, [200, 201])
        response_data = json.loads(response.data)
        self.assertTrue(response_data.get('success'))

    # ========================
    # ADDITIONAL: Message with only whitespace
    # ========================
    def test_send_message_whitespace_only(self):
        """Test that messages with only whitespace are rejected"""
        message_data = {
            'message': '   \t\n   ',  # Only whitespace
            'email': self.test_email,
            'name': self.test_name
        }
        
        response = self.client.post(
            '/api/chat/send',
            data=json.dumps(message_data),
            content_type='application/json'
        )
        
        # Should fail - whitespace only is treated as empty
        self.assertEqual(response.status_code, 400)

    # ========================
    # ADDITIONAL: Message without email/name
    # ========================
    def test_send_message_with_defaults(self):
        """Test that messages can be sent with default values for email/name"""
        
        # Message without email/name (should use defaults)
        message_data = {
            'message': 'Valid message without email/name'
            # email and name fields omitted
        }
        
        response = self.client.post(
            '/api/chat/send',
            data=json.dumps(message_data),
            content_type='application/json'
        )
        
        # Should succeed with default values
        self.assertIn(response.status_code, [200, 201])
        response_data = json.loads(response.data)
        self.assertTrue(response_data.get('success'))

    # ========================
    # ADDITIONAL: Retrieve sent messages
    # ========================
    def test_get_chat_messages_requires_admin_auth(self):
        """Test that getting messages requires admin authentication"""
        
        # Try to get messages without admin authentication
        response = self.client.get('/api/chat/messages')
        
        # Should fail - not authenticated as admin
        self.assertEqual(response.status_code, 401)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)


if __name__ == '__main__':
    unittest.main()
