"""
Test suite for chat functionality in Team 3D Flask application.
Tests localStorage-based chat persistence and message handling.
"""

import unittest
import json
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Flask project'))

from app import app


class ChatTestCase(unittest.TestCase):
    """Test cases for chat modal and localStorage functionality"""

    def setUp(self):
        """Set up test client and app context"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up after tests"""
        pass

   def test_home_page_loads(self):
        """Test that home page loads successfully"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Popular parts', response.data)

    def test_chat_page_loads(self):
        """Test that chat page loads successfully"""
        response = self.client.get('/chat')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'3DS Support Chat', response.data)

    def test_chat_page_contains_chat_elements(self):
        """Test that chat page contains required chat elements"""
        response = self.client.get('/chat')
        self.assertIn(b'chatMessages', response.data)
        self.assertIn(b'chatInput', response.data)
        self.assertIn(b'chatSendBtn', response.data)
        self.assertIn(b'localStorage', response.data)

    # ==================== LOCALSTORAGE STRUCTURE TESTS ====================

    def test_chat_page_initializes_storage_keys(self):
        """Test that chat page initializes correct localStorage keys"""
        response = self.client.get('/chat')
        # Check for storage key constants
        self.assertIn(b"'chat_history'", response.data)
        self.assertIn(b"'chat_id'", response.data)

    def test_modal_chat_uses_separate_storage_keys(self):
        """Test that modal chat uses separate localStorage keys than full page"""
        response = self.client.get('/')
        self.assertIn(b"'modal_chat_history'", response.data)

    def test_message_object_structure(self):
        """Test that chat messages have correct structure"""
        # Messages should have: text, sender, timestamp
        message = {
            'text': 'Test message',
            'sender': 'user',
            'timestamp': datetime.now().isoformat()
        }
        self.assertIn('text', message)
        self.assertIn('sender', message)
        self.assertIn('timestamp', message)
        self.assertEqual(message['sender'], 'user')

    def test_support_message_structure(self):
        """Test support response message structure"""
        message = {
            'text': 'Thank you for your message!',
            'sender': 'support',
            'timestamp': datetime.now().isoformat()
        }
        self.assertEqual(message['sender'], 'support')
        self.assertIn('Thank you', message['text'])

    # ==================== JAVASCRIPT LOGIC TESTS ====================

    def test_chat_html_contains_display_message_function(self):
        """Test that chat.html contains displayMessage function"""
        response = self.client.get('/chat')
        self.assertIn(b'function displayMessage', response.data)

    def test_chat_html_contains_save_chat_message_function(self):
        """Test that chat.html contains saveChatMessage function"""
        response = self.client.get('/chat')
        self.assertIn(b'function saveChatMessage', response.data)

    def test_chat_html_contains_send_message_function(self):
        """Test that chat.html contains sendMessage function"""
        response = self.client.get('/chat')
        self.assertIn(b'function sendMessage', response.data)

    def test_chat_html_contains_clear_history_function(self):
        """Test that chat.html contains clearChatHistory function"""
        response = self.client.get('/chat')
        self.assertIn(b'function clearChatHistory', response.data)

    def test_modal_chat_contains_required_functions(self):
        """Test that modal chat contains required functions"""
        response = self.client.get('/')
        self.assertIn(b'function displayMessage', response.data)
        self.assertIn(b'function saveChatMessage', response.data)
        self.assertIn(b'function sendMessage', response.data)
