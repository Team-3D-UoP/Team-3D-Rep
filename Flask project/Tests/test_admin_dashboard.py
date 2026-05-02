import os
import sys
import unittest

# Ensure project root is on sys.path so imports like `from app import app` work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class AdminDashboardTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def authenticate_admin(self):
        with self.client.session_transaction() as session:
            session['admin_authenticated'] = True
            session['admin_email'] = 'admin@example.com'

    def test_admin_dashboard_redirects_when_not_authenticated(self):
        rv = self.client.get('/admin')
        self.assertEqual(rv.status_code, 302)
        self.assertIn('/login', rv.headers.get('Location', ''))

    def test_admin_dashboard_renders_when_authenticated(self):
        self.authenticate_admin()
        rv = self.client.get('/admin')
        self.assertEqual(rv.status_code, 200)
        data = rv.data.decode('utf-8')
        self.assertIn('Admin Dashboard - Team 3D', data)
        self.assertIn('🔐 Admin Dashboard', data)
        self.assertIn('admin@example.com', data)
        self.assertIn('Welcome to the Team 3D Admin Portal', data)

    def test_admin_dashboard_contains_action_buttons(self):
        self.authenticate_admin()
        rv = self.client.get('/admin')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('Clear All Chats', data)
            self.assertIn('Logout', data)
            self.assertIn('clearAllChats()', data)
            self.assertIn('adminLogout()', data)

    def test_admin_dashboard_contains_stats_cards(self):
        self.authenticate_admin()
        rv = self.client.get('/admin')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('Total Users', data)
            self.assertIn('Total Products', data)
            self.assertIn('Total Reviews', data)
            self.assertIn('Active Carts', data)
            self.assertIn('totalUsers', data)
            self.assertIn('totalProducts', data)
            self.assertIn('totalReviews', data)
            self.assertIn('activeCarts', data)

    def test_admin_dashboard_contains_sections_and_containers(self):
        self.authenticate_admin()
        rv = self.client.get('/admin')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('Recent Reviews', data)
            self.assertIn('Recent Users', data)
            self.assertIn('Live Chat Messages', data)
            self.assertIn('reviews-container', data)
            self.assertIn('users-container', data)
            self.assertIn('users-list-container', data)
            self.assertIn('selected-user-info', data)
            self.assertIn('chat-container', data)
            self.assertIn('reply-input', data)

    def test_admin_dashboard_contains_dashboard_scripts(self):
        self.authenticate_admin()
        rv = self.client.get('/admin')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('function adminLogout()', data)
            self.assertIn('function clearAllChats()', data)
            self.assertIn('function loadDashboardData()', data)
            self.assertIn('function displayReviews(reviews)', data)
            self.assertIn('function loadUsersWithMessages()', data)
            self.assertIn('function displayUsersList(users)', data)
            self.assertIn('function selectUser(email, name)', data)
            self.assertIn('function loadChatMessagesForUser(userEmail)', data)
            self.assertIn('function displayChatMessages(messages)', data)
            self.assertIn('function deleteMessage(messageId)', data)
            self.assertIn('function sendAdminReply()', data)

    def test_admin_dashboard_contains_api_references(self):
        self.authenticate_admin()
        rv = self.client.get('/admin')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('/api/admin/logout', data)
            self.assertIn('/api/chat/clear-all', data)
            self.assertIn('/api/dashboard/users', data)
            self.assertIn('/api/dashboard/reviews', data)
            self.assertIn('/api/dashboard/carts', data)
            self.assertIn('/api/chat/messages', data)
            self.assertIn('/api/chat/delete/', data)
            self.assertIn('/api/chat/reply', data)

    def test_admin_dashboard_contains_data_loading_and_refresh(self):
        self.authenticate_admin()
        rv = self.client.get('/admin')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('Loading reviews...', data)
            self.assertIn('Loading users...', data)
            self.assertIn('No active chats', data)
            self.assertIn('window.addEventListener(\'DOMContentLoaded\'', data)
            self.assertIn('setInterval(loadChatMessages, 3000)', data)

    def test_admin_dashboard_contains_styling(self):
        self.authenticate_admin()
        rv = self.client.get('/admin')
        if rv.status_code == 200:
            data = rv.data.decode('utf-8')
            self.assertIn('.admin-container', data)
            self.assertIn('.admin-header', data)
            self.assertIn('.admin-grid', data)
            self.assertIn('.admin-card', data)
            self.assertIn('.admin-section', data)
            self.assertIn('.badge-user', data)
            self.assertIn('.badge-product', data)
            self.assertIn('.badge-seller', data)
            self.assertIn('@media (max-width: 768px)', data)


if __name__ == '__main__':
    unittest.main()
