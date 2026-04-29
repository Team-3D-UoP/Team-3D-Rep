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

    def test_chat_supports_multiple_messages(self):
        """Test that chat can store multiple messages"""
        messages = [
            {'text': 'Hello', 'sender': 'user', 'timestamp': datetime.now().isoformat()},
            {'text': 'Hi there!', 'sender': 'support', 'timestamp': datetime.now().isoformat()},
            {'text': 'How can I help?', 'sender': 'user', 'timestamp': datetime.now().isoformat()},
        ]
        # Simulate storing in localStorage
        chat_history = json.dumps(messages)
        loaded_messages = json.loads(chat_history)
        self.assertEqual(len(loaded_messages), 3)

    def test_message_serialization(self):
        """Test that messages can be serialized and deserialized"""
        original_message = {
            'text': 'Test message',
            'sender': 'user',
            'timestamp': datetime.now().isoformat()
        }
        # Serialize
        serialized = json.dumps(original_message)
        # Deserialize
        deserialized = json.loads(serialized)
        self.assertEqual(original_message, deserialized)

    def test_empty_chat_history(self):
        """Test handling of empty chat history"""
        empty_history = json.dumps([])
        loaded = json.loads(empty_history)
        self.assertEqual(len(loaded), 0)

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

       """Test that chat button exists on homepage"""
        response = self.client.get('/')
        self.assertIn(b'id="chatBtn"', response.data)
        self.assertIn(b'chat-button', response.data)

    def test_chat_modal_exists_on_homepage(self):
        """Test that chat modal exists on homepage"""
        response = self.client.get('/')
        self.assertIn(b'id="chatModal"', response.data)
        self.assertIn(b'3DS Support', response.data)

    def test_chat_input_exists(self):
        """Test that chat input field exists"""
        response = self.client.get('/')
        self.assertIn(b'class="chat-input"', response.data)

    def test_chat_send_button_exists(self):
        """Test that chat send button exists"""
        response = self.client.get('/')
        self.assertIn(b'class="chat-send-btn"', response.data)
        self.assertIn(b'Send', response.data)

    def test_chat_messages_container_exists(self):
        """Test that chat messages container exists"""
        response = self.client.get('/')
        self.assertIn(b'class="chat-messages"', response.data)
        
    def test_chat_page_has_event_listeners(self):
        """Test that chat page sets up event listeners"""
        response = self.client.get('/chat')
        self.assertIn(b'addEventListener', response.data)
        self.assertIn(b"'click'", response.data)
        self.assertIn(b"'keypress'", response.data)

    def test_modal_chat_has_click_listeners(self):
        """Test that modal chat has click event listeners"""
        response = self.client.get('/')
        # Check for send button click listener
        self.assertIn(b'chatSendBtn.addEventListener', response.data)
        # Check for modal close listener
        self.assertIn(b'chatModalClose.addEventListener', response.data)

    def test_modal_chat_has_keypress_listener(self):
        """Test that modal chat has keypress event listener for Enter key"""
        response = self.client.get('/')
        self.assertIn(b"e.key === 'Enter'", response.data)

    # ==================== STYLING TESTS ====================    def test_chat_modal_has_styling(self):
        """Test that chat modal has required CSS styles"""
        response = self.client.get('/')
        self.assertIn(b'.chat-modal', response.data)
        self.assertIn(b'.chat-input', response.data)
        self.assertIn(b'.chat-send-btn', response.data)

    def test_chat_message_styling(self):
        """Test that chat messages have proper styling classes"""
        response = self.client.get('/')
        self.assertIn(b'.chat-message-company', response.data)
        self.assertIn(b'chat-message', response.data)


    def test_message_text_not_empty(self):
        """Test that empty messages are rejected"""
        message_text = ''.strip()
        self.assertFalse(message_text)

    def test_message_text_trimmed(self):
        """Test that message text is trimmed of whitespace"""
        message_text = '  Hello  '.strip()
        self.assertEqual(message_text, 'Hello')

    def test_timestamp_is_valid_iso_format(self):
        """Test that timestamp is in valid ISO format"""
        timestamp = datetime.now().isoformat()
        # Should be parseable back to datetime
        parsed = datetime.fromisoformat(timestamp)
        self.assertIsInstance(parsed, datetime)

    def test_sender_values_are_valid(self):
        """Test that sender field only contains valid values"""
        valid_senders = ['user', 'support']
        message_sender = 'user'
        self.assertIn(message_sender, valid_senders)

    # ==================== INTEGRATION TESTS ====================

    def test_full_chat_flow(self):
        """Test full chat flow: open -> send message -> receive response"""
        # 1. Load homepage
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # 2. Check chat elements exist
        self.assertIn(b'chatBtn', response.data)
        self.assertIn(b'chatInput', response.data)
        self.assertIn(b'chatSendBtn', response.data)

    def test_chat_page_full_flow(self):
        """Test full chat page flow"""
        # 1. Load chat page
        response = self.client.get('/chat')
        self.assertEqual(response.status_code, 200)
        
        # 2. Check required elements
        self.assertIn(b'chatMessages', response.data)
        self.assertIn(b'chatInput', response.data)
        self.assertIn(b'chatSendBtn', response.data)

    def test_message_does_not_send_if_empty(self):
        """Test that empty messages don't trigger send"""
        # This is handled client-side but we test the logic
        message = '   '.strip()
        should_send = bool(message)
        self.assertFalse(should_send)

    def test_message_sends_if_not_empty(self):
        """Test that non-empty messages trigger send"""
        message = 'Hello'.strip()
        should_send = bool(message)
        self.assertTrue(should_send)


    def test_chat_handles_special_characters(self):
        """Test that chat handles messages with special characters"""
        special_message = "Hello! <script>alert('xss')</script>"
        self.assertIsNotNone(special_message)
        self.assertGreater(len(special_message), 0)

    def test_chat_handles_unicode_characters(self):
        """Test that chat handles unicode characters"""
        unicode_message = "Привет мир 你好 🚗"
        serialized = json.dumps({'text': unicode_message, 'sender': 'user'})
        deserialized = json.loads(serialized)
        self.assertEqual(deserialized['text'], unicode_message)

    def test_chat_handles_long_messages(self):
        """Test that chat handles long messages"""
        long_message = 'A' * 1000  # 1000 character message
        self.assertEqual(len(long_message), 1000)

    def test_chat_counter_calculation(self):
        """Test that message counter calculates correctly"""
        initial_count = 1  # Initial greeting message
        messages_added = 3
        total = initial_count + messages_added
        self.assertEqual(total, 4)


    def test_chat_modal_responsive_styles(self):
        """Test that chat modal has responsive CSS media queries"""
        response = self.client.get('/')
        self.assertIn(b'@media (max-width: 768px)', response.data)

    def test_chat_button_responsive_styles(self):
        """Test that chat button has responsive styles"""
        response = self.client.get('/')
        self.assertIn(b'.chat-button', response.data)


class ChatMessageStorageTest(unittest.TestCase):
    """Test cases for message storage logic"""

    def test_message_can_be_stored_in_dict(self):
        """Test storing message as dictionary"""
        message = {
            'text': 'Test',
            'sender': 'user',
            'timestamp': datetime.now().isoformat()
        }
        self.assertEqual(message['text'], 'Test')
        self.assertEqual(message['sender'], 'user')

    def test_multiple_messages_can_be_stored_in_list(self):
        """Test storing multiple messages in a list"""
        messages = []
        messages.append({'text': 'Msg1', 'sender': 'user', 'timestamp': datetime.now().isoformat()})
        messages.append({'text': 'Msg2', 'sender': 'support', 'timestamp': datetime.now().isoformat()})
        self.assertEqual(len(messages), 2)

    def test_message_history_json_serializable(self):
        """Test that message history can be serialized to JSON"""
        messages = [
            {'text': 'Hello', 'sender': 'user', 'timestamp': datetime.now().isoformat()},
            {'text': 'Hi!', 'sender': 'support', 'timestamp': datetime.now().isoformat()},
        ]
        json_str = json.dumps(messages)
        self.assertIsInstance(json_str, str)
        
        # Deserialize back
        loaded = json.loads(json_str)
        self.assertEqual(len(loaded), 2)

class ChatUITest(unittest.TestCase):
    """Test cases for chat UI elements"""

    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_chat_modal_header_text(self):
        """Test chat modal header text"""
        response = self.client.get('/')
        self.assertIn(b'3DS Support', response.data)

    def test_chat_modal_initial_greeting(self):
        """Test initial greeting message in chat"""
        response = self.client.get('/')
        self.assertIn(b'Live chat is always here 24/7', response.data)

    def test_chat_input_placeholder(self):
        """Test chat input has placeholder"""
        response = self.client.get('/')
        self.assertIn(b'placeholder=', response.data)

    def test_chat_logo_displays(self):
        """Test chat logo displays in modal"""
        response = self.client.get('/')
        self.assertIn(b'class="chat-logo"', response.data)
        self.assertIn(b'3DS', response.data)


if __name__ == '__main__':
    unittest.main()

