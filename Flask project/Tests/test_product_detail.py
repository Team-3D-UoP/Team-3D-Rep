import os
import sys
import unittest

# Add the Flask project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestProductDetailPage(unittest.TestCase):
    """Behavior-oriented tests for the `product_detail.html` route/template."""

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_product_detail_route_renders_existing_product(self):
        """GET /product/<id> should render known products."""
        response = self.client.get('/product/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Product Details', response.data)
        self.assertIn(b'Add to Cart', response.data)
        self.assertIn(b'Message Seller', response.data)

    def test_product_detail_route_returns_404_for_unknown_product(self):
        """GET /product/<id> should 404 for non-existent products."""
        response = self.client.get('/product/99999')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Product not found', response.data)

    def test_product_detail_contains_pricing_and_description_sections(self):
        """Template should include pricing and description structure."""
        response = self.client.get('/product/1')
        self.assertIn(b'Original Price:', response.data)
        self.assertIn(b'Discount:', response.data)
        self.assertIn(b'Final Price:', response.data)
        self.assertIn(b'Product Details', response.data)
        self.assertIn(b'features-list', response.data)

    def test_product_detail_contains_seller_area_and_links(self):
        """Seller info block and seller links should be present in template output."""
        response = self.client.get('/product/1')
        self.assertIn(b'Sold by', response.data)
        self.assertIn(b'seller-avatar', response.data)
        self.assertIn(b'seller-name-link', response.data)
        self.assertIn(b'/seller/', response.data)

    def test_product_detail_contains_chat_modal_shell(self):
        """Chat UI shell should be rendered on the page."""
        response = self.client.get('/product/1')
        self.assertIn(b'id="chatBtn"', response.data)
        self.assertIn(b'id="chatModal"', response.data)
        self.assertIn(b'id="chatModalClose"', response.data)
        self.assertIn(b'Team 3D Support', response.data)

    def test_product_detail_contains_review_sections_and_messages(self):
        """Review containers and fallback messages should exist."""
        response = self.client.get('/product/1')
        self.assertIn(b'Customer Reviews', response.data)
        self.assertIn(b'User Reviews', response.data)
        self.assertIn(b'id="userReviewsContainer"', response.data)
        self.assertIn(b'Loading reviews...', response.data)
        self.assertIn(b'No user reviews yet. Be the first to review!', response.data)

    def test_product_detail_shows_login_prompt_when_logged_out(self):
        """Logged-out users should see the login prompt variant."""
        response = self.client.get('/product/1')
        self.assertIn(b'Would you like to leave a review?', response.data)
        self.assertIn(b'Log in', response.data)
        self.assertIn(b'Sign up', response.data)

    def test_product_detail_shows_review_form_when_logged_in(self):
        """Logged-in users should see the interactive review form."""
        with self.client.session_transaction() as session:
            session['user_id'] = 'test-user-1'

        response = self.client.get('/product/1')
        self.assertIn(b'id="reviewForm"', response.data)
        self.assertIn(b'id="ratingInput"', response.data)
        self.assertIn(b'id="ratingValue"', response.data)
        self.assertIn(b'id="reviewText"', response.data)
        self.assertIn(b'Submit Review', response.data)

    def test_product_detail_defines_review_javascript_behaviors(self):
        """Review-related JS functions and handlers should be present."""
        response = self.client.get('/product/1')
        self.assertIn(b'document.getElementById(\'reviewForm\').addEventListener(\'submit\'', response.data)
        self.assertIn(b'async function loadUserReviews()', response.data)
        self.assertIn(b'async function deleteReview(reviewId)', response.data)
        self.assertIn(b'function escapeHtml(text)', response.data)
        self.assertIn(b'loadUserReviews();', response.data)

    def test_product_detail_uses_expected_review_and_cart_endpoints(self):
        """Script should reference review/cart endpoints used by this page."""
        response = self.client.get('/product/1')
        self.assertIn(b'/product/1/review', response.data)
        self.assertIn(b'/product/1/reviews', response.data)
        self.assertIn(b"fetch('/api/cart'", response.data)
        self.assertIn(b'part_id: productId', response.data)

    def test_product_detail_defines_chat_behaviors(self):
        """Chat JS functions and API calls should exist in the page script."""
        response = self.client.get('/product/1')
        self.assertIn(b'function initializeChatElements()', response.data)
        self.assertIn(b'function attachChatListeners()', response.data)
        self.assertIn(b'function getCurrentUserInfo()', response.data)
        self.assertIn(b'async function loadChatHistoryFromStorage()', response.data)
        self.assertIn(b'function sendMessage()', response.data)
        self.assertIn(b'function isUserLoggedIn()', response.data)
        self.assertIn(b'function showLoginRequired()', response.data)
        self.assertIn(b"fetch('/api/chat/send'", response.data)
        self.assertIn(b"fetch('/api/chat/get-customer-messages')", response.data)

    def test_product_detail_message_seller_flow_is_defined(self):
        """Message-seller helper should guard login and prefill message."""
        response = self.client.get('/product/1')
        self.assertIn(b'function messageSellerFromProduct()', response.data)
        self.assertIn(b'if (!isUserLoggedIn())', response.data)
        self.assertIn(b'chatBtn.click();', response.data)
        self.assertIn(b'chatInput.value = message;', response.data)

    def test_product_detail_review_rating_interaction_script_exists(self):
        """Rating-star click/hover/mouseleave behavior should be scripted."""
        response = self.client.get('/product/1')
        self.assertIn(b"const stars = document.querySelectorAll('.rating-star');", response.data)
        self.assertIn(b"star.addEventListener('click'", response.data)
        self.assertIn(b"star.addEventListener('mouseover'", response.data)
        self.assertIn(b"document.getElementById('ratingInput').addEventListener('mouseleave'", response.data)
        self.assertIn(b"ratingValue.value = rating;", response.data)

    def test_product_detail_review_submit_validation_messages_exist(self):
        """Review submit validation and error messaging should be present."""
        response = self.client.get('/product/1')
        self.assertIn(b'Please provide both a rating and review text.', response.data)
        self.assertIn(b'Error submitting review. Please try again.', response.data)
        self.assertIn(b"document.getElementById('successMessage').style.display = 'block';", response.data)

    def test_product_detail_delete_review_requires_authentication(self):
        """Deleting a review without session user_id should be unauthorized."""
        response = self.client.delete('/product/1/review/1')
        self.assertEqual(response.status_code, 401)

    def test_product_detail_get_reviews_endpoint_shape(self):
        """Product review endpoint should return a JSON payload with review collection."""
        response = self.client.get('/product/1/reviews')
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIsInstance(payload, dict)
        self.assertIn('reviews', payload)
        self.assertIn('count', payload)

    def test_product_detail_add_to_cart_api_success(self):
        """Cart API used by product_detail should accept valid payload."""
        response = self.client.post('/api/cart', json={'part_id': 1, 'quantity': 1})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload.get('success'))
        self.assertIn('cart_count', payload)

    def test_product_detail_add_to_cart_api_validation_errors(self):
        """Cart API should reject malformed payloads."""
        missing_part_id = self.client.post('/api/cart', json={'quantity': 1})
        self.assertEqual(missing_part_id.status_code, 400)

        invalid_part_id = self.client.post('/api/cart', json={'part_id': 'abc', 'quantity': 1})
        self.assertEqual(invalid_part_id.status_code, 400)

    def test_product_detail_chat_login_modal_strings_exist(self):
        """Chat login-required modal and helper text should be present."""
        response = self.client.get('/product/1')
        self.assertIn(b'Login Required', response.data)
        self.assertIn(b'Please log in first to use the chat feature', response.data)
        self.assertIn(b"window.location.href='/login'", response.data)


if __name__ == '__main__':
    unittest.main()
