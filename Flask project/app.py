import os
import sqlite3
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from data.products import OFFER_PRODUCTS
from data.sellers import SELLERS_DATA
from data.reviews import REVIEWS_DATA
from io import BytesIO
from PIL import Image, ImageDraw
import base64
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv
from datetime import datetime
import requests
from models import db, ProductReview, SellerReview, CartItem, Part, User, ChatMessage
from db_registrations import *  # noqa: F401,F403 - Required for select_user_id, insert_* functions

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///team3d.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

CORS(app, supports_credentials=True)

# Create database tables
with app.app_context():
    db.create_all()

# Firebase Configuration
FIREBASE_DATABASE_URL = 'https://team-3d-default-rtdb.europe-west1.firebasedatabase.app'

# Initialize Firebase Auth - Optional, gracefully handles if not configured
firebase_initialized = False
try:
    cred_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        firebase_initialized = True
        print("✓ Firebase Admin SDK initialized with serviceAccountKey.json")
    else:
        print("⚠ serviceAccountKey.json not found - Using client-side Firebase auth")
except Exception as e:
    print(f"⚠ Firebase initialization error: {e}")

print(f"✓ Firebase Realtime Database connected: {FIREBASE_DATABASE_URL}")


# Firebase Realtime Database Helper Functions (Using REST API - No Secret Key Needed!)
def save_user_to_firebase(uid, email, username, fullname):
    """Save user profile to Firebase Realtime Database using REST API"""
    try:
        user_data = {
            'email': email,
            'username': username,
            'fullname': fullname,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        url = f"{FIREBASE_DATABASE_URL}/users/{uid}.json"
        response = requests.put(url, json=user_data, timeout=5)

        if response.status_code in [200, 201]:
            print(f"✓ User saved to Firebase: {email}")
            return True
        else:
            print(f"⚠ Error saving user to Firebase: {response.status_code} {response.text}")
            return False
    except Exception as e:
        print(f"⚠ Error saving user to Firebase: {e}")
        return False


def get_user_from_firebase(uid):
    """Get user profile from Firebase using REST API"""
    try:
        url = f"{FIREBASE_DATABASE_URL}/users/{uid}.json"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"⚠ Error getting user from Firebase: {e}")
        return None


def save_review_to_firebase(review_type, item_id, uid, email, name, rating, text):
    """Save review to Firebase using REST API"""
    try:
        review_data = {
            'item_id': item_id,
            'user_id': uid,
            'user_email': email,
            'user_name': name,
            'rating': rating,
            'review_text': text,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        url = f"{FIREBASE_DATABASE_URL}/reviews/{review_type}/{item_id}/{uid}.json"
        response = requests.put(url, json=review_data, timeout=5)

        if response.status_code in [200, 201]:
            print("✓ Review saved to Firebase")
            return True
        else:
            print(f"⚠ Error saving review to Firebase: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠ Error saving review to Firebase: {e}")
        return False


def get_reviews_from_firebase(review_type, item_id):
    """Get all reviews for an item from Firebase using REST API"""
    try:
        url = f"{FIREBASE_DATABASE_URL}/reviews/{review_type}/{item_id}.json"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            reviews_data = response.json()
            if not reviews_data:
                return []
            return list(reviews_data.values())
        return []
    except Exception as e:
        print(f"⚠ Error getting reviews from Firebase: {e}")
        return []


def save_cart_item_to_firebase(uid, product_id, quantity):
    """Save cart item to Firebase using REST API"""
    try:
        cart_data = {
            'product_id': product_id,
            'quantity': quantity,
            'updated_at': datetime.utcnow().isoformat()
        }
        url = f"{FIREBASE_DATABASE_URL}/carts/{uid}/{product_id}.json"
        response = requests.put(url, json=cart_data, timeout=5)

        if response.status_code in [200, 201]:
            print("✓ Cart item saved to Firebase")
            return True
        else:
            print(f"⚠ Error saving cart to Firebase: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠ Error saving cart to Firebase: {e}")
        return False


def get_cart_from_firebase(uid):
    """Get cart items from Firebase using REST API"""
    try:
        url = f"{FIREBASE_DATABASE_URL}/carts/{uid}.json"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            cart_data = response.json()
            if not cart_data:
                return {}
            return cart_data
        return {}
    except Exception as e:
        print(f"⚠ Error getting cart from Firebase: {e}")
        return {}


def _get_seller_for_product(product):
    """Return the seller assigned to a given product.

    Uses a deterministic mapping based on the product id so that a seller's
    profile page consistently lists the same products that were attributed to
    them on the homepage / product detail pages.
    """
    if not SELLERS_DATA:
        return None
    return SELLERS_DATA[(product['id'] - 1) % len(SELLERS_DATA)]


def _get_products_for_seller(seller_id):
    """Return all products attributed to the given seller (deterministic)."""
    return [p for p in OFFER_PRODUCTS if _get_seller_for_product(p)['id'] == seller_id]


def _get_reviews_for_seller(seller_id):
    """Return a deterministic slice of reviews for a given seller.

    Until we wire up a real reviews-by-seller table, we deal each seller a
    rotating subset of REVIEWS_DATA so every seller's profile shows feedback.
    """
    if not REVIEWS_DATA:
        return []
    n = len(REVIEWS_DATA)
    # Take a window of up to 4 reviews starting at an offset based on the seller id.
    offset = (seller_id - 1) % n
    return [REVIEWS_DATA[(offset + i) % n] for i in range(min(4, n))]


@app.route("/", methods=['GET'])
def home():
    # Assign sellers to each product (deterministic so seller profile matches).
    products_with_sellers = []
    for product in OFFER_PRODUCTS:
        product_with_seller = product.copy()
        product_with_seller['seller'] = _get_seller_for_product(product)
        products_with_sellers.append(product_with_seller)

    return render_template("main_homepage.html",
                         offer_products=products_with_sellers,
                         reviews=REVIEWS_DATA)

@app.route("/product/<int:product_id>", methods=['GET'])
def product_detail(product_id):
    # Find the product by ID
    product = next((p for p in OFFER_PRODUCTS if p['id'] == product_id), None)

    if not product:
        return "Product not found", 404

    # Use deterministic seller mapping so it matches the homepage and seller page.
    product_with_seller = product.copy()
    product_with_seller['seller'] = _get_seller_for_product(product)

    return render_template("product_detail.html", product=product_with_seller)


@app.route("/seller/<int:seller_id>", methods=['GET'])
def seller_detail(seller_id):
    seller = next((s for s in SELLERS_DATA if s['id'] == seller_id), None)
    if not seller:
        return "Seller not found", 404

    seller_products = _get_products_for_seller(seller_id)
    seller_reviews = _get_reviews_for_seller(seller_id)

    return render_template("seller_detail.html",
                           seller=seller,
                           products=seller_products,
                           reviews=seller_reviews)


@app.route("/seller/<int:seller_id>/review", methods=['POST'])
def submit_seller_review(seller_id):
    """Submit a review for a seller"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    # Get the review data
    data = request.get_json(silent=True)

    if not data or 'rating' not in data or 'review_text' not in data:
        return jsonify({"error": "Missing review data"}), 400

    try:
        rating = int(data['rating'])
        review_text = data['review_text'].strip()

        if rating < 1 or rating > 5:
            return jsonify({"error": "Invalid rating"}), 400

        if not review_text or len(review_text) < 10:
            return jsonify({"error": "Review must be at least 10 characters"}), 400

        # Check if seller exists
        seller = next((s for s in SELLERS_DATA if s['id'] == seller_id), None)
        if not seller:
            return jsonify({"error": "Seller not found"}), 404

        # Check if user already reviewed this seller
        existing_review = SellerReview.query.filter_by(
            seller_id=seller_id,
            user_id=session['user_id']
        ).first()

        if existing_review:
            # Update existing review
            existing_review.rating = rating
            existing_review.review_text = review_text
            db.session.commit()

            # Also save to Firebase
            save_review_to_firebase('seller', seller_id, session['user_id'],
                                   session.get('email', ''), session.get('name', 'Anonymous'),
                                   rating, review_text)

            return jsonify({
                "success": True,
                "message": "Review updated successfully",
                "review_id": existing_review.id
            }), 200
        else:
            # Create new review
            new_review = SellerReview(
                seller_id=seller_id,
                user_id=session['user_id'],
                user_email=session.get('email', ''),
                user_name=session.get('name', 'Anonymous'),
                rating=rating,
                review_text=review_text
            )
            db.session.add(new_review)
            db.session.commit()

            # Also save to Firebase
            save_review_to_firebase('seller', seller_id, session['user_id'],
                                   session.get('email', ''), session.get('name', 'Anonymous'),
                                   rating, review_text)

            return jsonify({
                "success": True,
                "message": "Review submitted successfully",
                "review_id": new_review.id
            }), 201

    except (ValueError, TypeError) as e:
        print(f"ValueError/TypeError in submit_seller_review: {str(e)}")
        return jsonify({"error": "Invalid data format"}), 400
    except Exception as e:
        print(f"Exception in submit_seller_review: {str(e)}")
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error: {str(e)}"}), 500


@app.route("/account/<int:seller_id>/reviews", methods=['GET'])
def get_seller_reviews(seller_id):
    """Get all user reviews for a seller"""
    try:
        reviews = SellerReview.query.filter_by(seller_id=seller_id).order_by(
            SellerReview.created_at.desc()
        ).all()

        return jsonify({
            "success": True,
            "reviews": [review.to_dict() for review in reviews],
            "count": len(reviews)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/user/reviews", methods=['GET'])
def get_user_reviews():
    """Get all reviews submitted by the current user (both product and seller reviews from Firebase)"""
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    try:
        uid = session['user_id']
        product_reviews_data = []
        seller_reviews_data = []

        # Get all product reviews from Firebase
        try:
            url = f"{FIREBASE_DATABASE_URL}/reviews/product.json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                all_products = response.json()
                if all_products:
                    for product_id, reviews in all_products.items():
                        if isinstance(reviews, dict) and uid in reviews:
                            review = reviews[uid]
                            product = next((p for p in OFFER_PRODUCTS if p['id'] == review.get('item_id')), None)
                            if product:
                                review_data = {
                                    'id': f"{product_id}_{uid}",
                                    'type': 'product',
                                    'item_name': product['name'],
                                    'item_id': product_id,
                                    'rating': review.get('rating', 0),
                                    'review_text': review.get('review_text', ''),
                                    'created_at': review.get('created_at', ''),
                                    'user_name': review.get('user_name', 'Anonymous')
                                }
                                product_reviews_data.append(review_data)
        except Exception as e:
            print(f"Error getting product reviews from Firebase: {e}")

        # Get all seller reviews from Firebase
        try:
            url = f"{FIREBASE_DATABASE_URL}/reviews/seller.json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                all_sellers = response.json()
                if all_sellers:
                    for seller_id, reviews in all_sellers.items():
                        if isinstance(reviews, dict) and uid in reviews:
                            review = reviews[uid]
                            seller = next((s for s in SELLERS_DATA if s['id'] == review.get('item_id')), None)
                            if seller:
                                review_data = {
                                    'id': f"{seller_id}_{uid}",
                                    'type': 'seller',
                                    'item_name': seller['name'],
                                    'item_id': seller_id,
                                    'rating': review.get('rating', 0),
                                    'review_text': review.get('review_text', ''),
                                    'created_at': review.get('created_at', ''),
                                    'user_name': review.get('user_name', 'Anonymous')
                                }
                                seller_reviews_data.append(review_data)
        except Exception as e:
            print(f"Error getting seller reviews from Firebase: {e}")

        # Combine and sort by date
        all_reviews = product_reviews_data + seller_reviews_data
        all_reviews.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        return jsonify({
            "success": True,
            "reviews": all_reviews,
            "product_reviews_count": len(product_reviews_data),
            "seller_reviews_count": len(seller_reviews_data),
            "total_count": len(all_reviews)
        }), 200

    except Exception as e:
        print(f"Error in get_user_reviews: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/product/<int:product_id>/review", methods=['POST'])
def submit_review(product_id):
    """Submit a review for a product"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    # Get the review data
    data = request.get_json(silent=True)

    if not data or 'rating' not in data or 'review_text' not in data:
        return jsonify({"error": "Missing review data"}), 400

    try:
        rating = int(data['rating'])
        review_text = data['review_text'].strip()

        if rating < 1 or rating > 5:
            return jsonify({"error": "Invalid rating"}), 400

        if not review_text or len(review_text) < 10:
            return jsonify({"error": "Review must be at least 10 characters"}), 400

        # Check if product exists
        product = next((p for p in OFFER_PRODUCTS if p['id'] == product_id), None)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        # Check if user already reviewed this product
        existing_review = ProductReview.query.filter_by(
            product_id=product_id,
            user_id=session['user_id']
        ).first()

        if existing_review:
            # Update existing review
            existing_review.rating = rating
            existing_review.review_text = review_text
            db.session.commit()

            # Also save to Firebase
            save_review_to_firebase('product', product_id, session['user_id'],
                                   session.get('email', ''), session.get('name', 'Anonymous'),
                                   rating, review_text)

            return jsonify({
                "success": True,
                "message": "Review updated successfully",
                "review_id": existing_review.id
            }), 200
        else:
            # Create new review
            new_review = ProductReview(
                product_id=product_id,
                user_id=session['user_id'],
                user_email=session.get('email', ''),
                user_name=session.get('name', 'Anonymous'),
                rating=rating,
                review_text=review_text
            )
            db.session.add(new_review)
            db.session.commit()

            # Also save to Firebase
            save_review_to_firebase('product', product_id, session['user_id'],
                                   session.get('email', ''), session.get('name', 'Anonymous'),
                                   rating, review_text)

            return jsonify({
                "success": True,
                "message": "Review submitted successfully",
                "review_id": new_review.id
            }), 201

    except (ValueError, TypeError) as e:
        print(f"ValueError/TypeError in submit_review: {str(e)}")
        return jsonify({"error": "Invalid data format"}), 400
    except Exception as e:
        print(f"Exception in submit_review: {str(e)}")
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error: {str(e)}"}), 500


@app.route("/product/<int:product_id>/reviews", methods=['GET'])
def get_product_reviews(product_id):
    """Get all reviews for a product"""
    try:
        reviews = ProductReview.query.filter_by(product_id=product_id).order_by(
            ProductReview.created_at.desc()
        ).all()

        return jsonify({
            "success": True,
            "reviews": [review.to_dict() for review in reviews],
            "count": len(reviews)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/product/<int:product_id>/review/<int:review_id>", methods=['DELETE'])
def delete_review(product_id, review_id):
    """Delete a review (only by the user who posted it)"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    try:
        review = ProductReview.query.filter_by(
            id=review_id,
            product_id=product_id
        ).first()

        if not review:
            return jsonify({"error": "Review not found"}), 404

        # Check if user owns this review
        if review.user_id != session['user_id']:
            return jsonify({"error": "You can only delete your own reviews"}), 403

        db.session.delete(review)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Review deleted successfully"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/cart/add", methods=['POST'])
def add_to_cart():
    """Add an item to the user's cart"""
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    try:
        data = request.get_json(silent=True)

        if not data or 'product_id' not in data:
            return jsonify({"error": "Product ID is required"}), 400

        product_id = int(data['product_id'])
        quantity = int(data.get('quantity', 1))

        if quantity < 1:
            return jsonify({"error": "Quantity must be at least 1"}), 400

        # Check if product exists
        product = next((p for p in OFFER_PRODUCTS if p['id'] == product_id), None)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        # Check if item already in cart
        existing_item = CartItem.query.filter_by(
            user_id=session['user_id'],
            product_id=product_id
        ).first()

        if existing_item:
            # Update quantity
            existing_item.quantity += quantity
            db.session.commit()

            # Also save to Firebase
            save_cart_item_to_firebase(session['user_id'], product_id, existing_item.quantity)

            return jsonify({
                "success": True,
                "message": "Item quantity updated",
                "item_id": existing_item.id
            }), 200
        else:
            # Create new cart item
            new_item = CartItem(
                user_id=session['user_id'],
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(new_item)
            db.session.commit()

            # Also save to Firebase
            save_cart_item_to_firebase(session['user_id'], product_id, quantity)

            return jsonify({
                "success": True,
                "message": "Item added to cart",
                "item_id": new_item.id
            }), 201

    except (ValueError, TypeError):
        return jsonify({"error": "Invalid data format"}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error in add_to_cart: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/cart", methods=['GET'])
def get_cart():
    """Get all items in user's cart"""
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    try:
        cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()

        items_with_details = []
        for item in cart_items:
            product = next((p for p in OFFER_PRODUCTS if p['id'] == item.product_id), None)
            if product:
                item_data = item.to_dict()
                item_data['product'] = product
                item_data['total_price'] = product['current_price'] * item.quantity
                items_with_details.append(item_data)

        total_price = sum(item['total_price'] for item in items_with_details)

        return jsonify({
            "success": True,
            "items": items_with_details,
            "count": len(items_with_details),
            "total_price": total_price
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cart/item/<int:item_id>", methods=['DELETE'])
def remove_from_cart(item_id):
    """Remove an item from the user's cart"""
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    try:
        cart_item = CartItem.query.filter_by(
            id=item_id,
            user_id=session['user_id']
        ).first()

        if not cart_item:
            return jsonify({"error": "Cart item not found"}), 404

        db.session.delete(cart_item)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Item removed from cart"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/cart/item/<int:item_id>", methods=['PUT'])
def update_cart_item(item_id):
    """Update quantity of an item in the cart"""
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    try:
        data = request.get_json(silent=True)

        if not data or 'quantity' not in data:
            return jsonify({"error": "Quantity is required"}), 400

        quantity = int(data['quantity'])

        if quantity < 1:
            return jsonify({"error": "Quantity must be at least 1"}), 400

        cart_item = CartItem.query.filter_by(
            id=item_id,
            user_id=session['user_id']
        ).first()

        if not cart_item:
            return jsonify({"error": "Cart item not found"}), 404

        cart_item.quantity = quantity
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Cart item updated"
        }), 200

    except ValueError:
        return jsonify({"error": "Invalid quantity format"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/cart", methods=['GET'])
def view_cart():
    """Display the shopping cart page"""
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    return render_template("cart.html")


@app.route("/api/calc_tax", methods=['GET', 'POST'])
def calc_tax():
    if request.method == 'POST':
        data = request.get_json(silent=True)

        if not data or "a" not in data or "b" not in data:
            return jsonify({"error1": "Income can not be blank"}), 400

        try:
            a = float(data["a"])
            b = float(data["b"])
            session['empl'] = a
            session['savings'] = b
        except (ValueError, TypeError):
            return jsonify({"error4": "Both incomes must be numerical"}), 400

        return render_template("index.html")

@app.route('/confirm', methods=["GET"])
def confirm_page():
    return render_template("confirm.html")

@app.route("/api/saveTax", methods=["POST"])
def save_incomes():
    data = request.get_json(silent=True)

    try:
        a = float(data["a"])
        b = float(data["b"])

        import db_incomeManager
        db_incomeManager.addIncomes(1, a, b)

        if a < 0 or b < 0:
            return jsonify({"error2": "Please provide positive income"}), 400

        if b < 1000:
            return jsonify({"taxIncome": 20/100*a, "taxSavings": 0, "message":"Saved"}), 200

        return jsonify({"taxIncome": 20/100*a, "taxSavings": 15/100*(b-1000), "message":"Saved"}), 200

    except (ValueError, TypeError):
        return jsonify({"error": "Error saving"}), 400

@app.route("/api/placeholder-image/<part_name>", methods=['GET'])
def placeholder_image(part_name):
    img = Image.new('RGB', (120, 120), color='#f0f0f0')
    draw = ImageDraw.Draw(img)
    draw.text((10, 50), part_name[:15], fill='#003d7a')

    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode()

    return f"data:image/png;base64,{img_base64}"

# Admin Credentials
ADMIN_EMAIL = "adminpage@gmail.com"
ADMIN_PASSWORD = "Admin123"

@app.route("/login", methods=['GET'])
def login():
    return render_template("login_screen.html")

@app.route("/admin-login", methods=['GET'])
def admin_login_page():
    """Admin login page"""
    return render_template("admin_login_page.html")

@app.route("/api/admin/login", methods=['POST'])
def admin_login():
    """Admin authentication endpoint"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # Verify admin credentials
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['admin_authenticated'] = True
            session['admin_email'] = email
            session['admin_logged_in_at'] = datetime.utcnow().isoformat()

            print(f"✓ Admin logged in: {email}")
            return jsonify({
                "success": True,
                "message": "Admin login successful",
                "redirect": "/admin"
            }), 200
        else:
            print(f"✗ Admin login failed for: {email}")
            return jsonify({"error": "Invalid admin credentials"}), 401

    except Exception as e:
        print(f"Admin login error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/admin", methods=['GET'])
def admin_dashboard():
    """Admin dashboard page"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('login'))

    return render_template("admin_dashboard.html",
                         admin_email=session.get('admin_email'))

@app.route("/api/admin/logout", methods=['POST'])
def admin_logout():
    """Admin logout"""
    session.clear()
    return jsonify({"success": True, "message": "Logged out"}), 200

@app.route("/api/dashboard/users", methods=['GET'])
def dashboard_users():
    """Get user statistics for admin dashboard"""
    if not session.get('admin_authenticated'):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        users = User.query.all()
        return jsonify({
            "count": len(users),
            "users": [u.to_dict() for u in users]
        }), 200
    except Exception as e:
        print(f"Error fetching users: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/dashboard/reviews", methods=['GET'])
def dashboard_reviews():
    """Get review statistics for admin dashboard"""
    if not session.get('admin_authenticated'):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        product_reviews = ProductReview.query.all()
        seller_reviews = SellerReview.query.all()

        all_reviews = []

        # Add product reviews
        for review in product_reviews:
            all_reviews.append({
                'id': review.id,
                'type': 'product',
                'user_name': review.user_name,
                'rating': review.rating,
                'review_text': review.review_text,
                'created_at': review.created_at.isoformat()
            })

        # Add seller reviews
        for review in seller_reviews:
            all_reviews.append({
                'id': review.id,
                'type': 'seller',
                'user_name': review.user_name,
                'rating': review.rating,
                'review_text': review.review_text,
                'created_at': review.created_at.isoformat()
            })

        # Sort by date, most recent first
        all_reviews.sort(key=lambda x: x['created_at'], reverse=True)

        return jsonify({
            "count": len(all_reviews),
            "reviews": all_reviews
        }), 200
    except Exception as e:
        print(f"Error fetching reviews: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/dashboard/carts", methods=['GET'])
def dashboard_carts():
    """Get cart statistics for admin dashboard"""
    if not session.get('admin_authenticated'):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        carts = CartItem.query.all()
        total_items = sum(cart.quantity for cart in carts)

        return jsonify({
            "count": total_items,
            "cart_count": len(carts)
        }), 200
    except Exception as e:
        print(f"Error fetching carts: {e}")
        return jsonify({"error": str(e)}), 500

# Chat API Endpoints (Using Firebase for real-time sync across computers)
@app.route("/api/chat/send", methods=['POST'])
def send_chat_message():
    """Send a chat message from customer"""
    try:
        print("📨 Chat send request received")

        data = request.get_json()
        print(f"Request data: {data}")

        message = data.get('message', '').strip()
        user_email = data.get('email', 'Anonymous')
        user_name = data.get('name', 'Anonymous')

        print(f"Message: {message}, Email: {user_email}, Name: {user_name}")

        if not message or len(message) < 1:
            print("❌ Message is empty")
            return jsonify({"error": "Message cannot be empty"}), 400

        # Save to Firebase (accessible from any computer!)
        chat_data = {
            'user_email': user_email,
            'user_name': user_name,
            'message': message,
            'sender_type': 'customer',
            'created_at': datetime.utcnow().isoformat()
        }

        timestamp = int(datetime.utcnow().timestamp() * 1000)  # Use milliseconds for better uniqueness
        url = f"{FIREBASE_DATABASE_URL}/chat/{timestamp}.json"

        print(f"📤 Saving to Firebase: {url}")
        print(f"Data: {chat_data}")

        response = requests.put(url, json=chat_data, timeout=5)

        print(f"Firebase response status: {response.status_code}")
        print(f"Firebase response: {response.text}")

        if response.status_code in [200, 201]:
            print(f"✓ Chat message saved to Firebase from {user_name}")
            return jsonify({
                "success": True,
                "created_at": chat_data['created_at']
            }), 201
        else:
            print(f"⚠ Error saving to Firebase: {response.status_code} - {response.text}")
            return jsonify({"error": f"Failed to save message: {response.status_code}"}), 500

    except Exception as e:
        print(f"❌ Error saving chat message: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/chat/messages", methods=['GET'])
def get_chat_messages():
    """Get all chat messages from Firebase (for admin)"""
    if not session.get('admin_authenticated'):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # Fetch all messages from Firebase
        url = f"{FIREBASE_DATABASE_URL}/chat.json"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            messages_data = response.json()
            if not messages_data:
                return jsonify({
                    "success": True,
                    "count": 0,
                    "messages": []
                }), 200

            # Convert Firebase object to array and sort by timestamp
            messages = []
            for timestamp, msg_data in messages_data.items():
                msg_data['id'] = timestamp
                messages.append(msg_data)

            # Sort by created_at descending (newest first)
            messages.sort(key=lambda x: x.get('created_at', ''), reverse=True)

            return jsonify({
                "success": True,
                "count": len(messages),
                "messages": messages
            }), 200
        else:
            return jsonify({
                "success": True,
                "count": 0,
                "messages": []
            }), 200

    except Exception as e:
        print(f"Error fetching chat messages from Firebase: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/chat/reply", methods=['POST'])
def reply_to_chat():
    """Admin reply to a chat message (save to Firebase)"""
    print(f"📨 Chat reply request - Session: {dict(session)}")
    print(f"admin_authenticated: {session.get('admin_authenticated')}")

    if not session.get('admin_authenticated'):
        print("❌ Unauthorized: admin_authenticated not in session")
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        target_user_email = data.get('target_user_email', '').strip()

        if not message or len(message) < 1:
            return jsonify({"error": "Message cannot be empty"}), 400

        # Save admin reply to Firebase - now with target user
        chat_data = {
            'user_name': 'Admin Support',
            'user_email': session.get('admin_email'),
            'message': message,
            'sender_type': 'admin',
            'target_user_email': target_user_email,  # Only visible to this user
            'created_at': datetime.utcnow().isoformat()
        }

        timestamp = int(datetime.utcnow().timestamp() * 1000)  # Convert to milliseconds integer
        url = f"{FIREBASE_DATABASE_URL}/chat/{timestamp}.json"
        print(f"📤 Saving reply to Firebase: {url}")
        print(f"📦 Data: {chat_data}")

        response = requests.put(url, json=chat_data, timeout=5)

        if response.status_code in [200, 201]:
            print(f"✓ Admin reply saved to Firebase for {target_user_email}")
            return jsonify({
                "success": True,
                "created_at": chat_data['created_at']
            }), 201
        else:
            print(f"⚠ Error saving reply to Firebase: {response.status_code}")
            print(f"Firebase response: {response.text}")
            return jsonify({"error": "Failed to save reply"}), 500

    except Exception as e:
        print(f"Error saving admin reply: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/chat/delete/<message_id>", methods=['DELETE'])
def delete_chat_message(message_id):
    """Delete a chat message from Firebase (admin only)"""
    if not session.get('admin_authenticated'):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # Delete message from Firebase using REST API
        url = f"{FIREBASE_DATABASE_URL}/chat/{message_id}.json"
        response = requests.delete(url, timeout=5)

        if response.status_code in [200, 204]:
            print(f"✓ Chat message deleted: {message_id}")
            return jsonify({"success": True, "message": "Message deleted"}), 200
        else:
            print(f"⚠ Error deleting message from Firebase: {response.status_code}")
            return jsonify({"error": "Failed to delete message"}), 500

    except Exception as e:
        print(f"Error deleting chat message: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/chat/clear-all", methods=['POST'])
def clear_all_chats():
    """Clear all chat messages from Firebase (admin only)"""
    if not session.get('admin_authenticated'):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # Delete all messages from Firebase
        url = f"{FIREBASE_DATABASE_URL}/chat.json"
        response = requests.delete(url, timeout=5)

        if response.status_code in [200, 204]:
            print("✓ All chat messages cleared")
            return jsonify({"success": True, "message": "All chats cleared"}), 200
        else:
            print(f"⚠ Error clearing chats from Firebase: {response.status_code}")
            return jsonify({"error": "Failed to clear chats"}), 500

    except Exception as e:
        print(f"Error clearing chats: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/chat/get-customer-messages", methods=['GET'])
def get_customer_messages():
    """Get all chat messages for customer (from Firebase)"""
    try:
        # Fetch all messages from Firebase
        url = f"{FIREBASE_DATABASE_URL}/chat.json"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            messages_data = response.json()
            if not messages_data:
                return jsonify({
                    "success": True,
                    "messages": []
                }), 200

            # Convert Firebase object to array and sort by timestamp
            messages = []
            for timestamp, msg_data in messages_data.items():
                messages.append(msg_data)

            # Sort by created_at ascending (oldest first)
            messages.sort(key=lambda x: x.get('created_at', ''))

            return jsonify({
                "success": True,
                "messages": messages
            }), 200
        else:
            return jsonify({
                "success": True,
                "messages": []
            }), 200

    except Exception as e:
        print(f"Error fetching customer messages from Firebase: {e}")
        return jsonify({
            "success": True,
            "messages": []
        }), 200

@app.route("/api/chat/unread-count", methods=['GET'])
def unread_chat_count():
    """Get count of unread chat messages (for admin)"""
    if not session.get('admin_authenticated'):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        unread = ChatMessage.query.filter_by(is_read=False, sender_type='customer').count()
        return jsonify({
            "success": True,
            "unread_count": unread
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register_screen.html")

    if not firebase_initialized:
        return jsonify({"error": "Firebase not configured on this server"}), 503

    try:
        data = request.get_json() or request.form
        email = data.get('email')
        password = data.get('password')
        fullname = data.get('fullname')
        username = data.get('username')

        if not all([email, password, fullname, username]):
            return jsonify({"error": "All fields are required"}), 400

        user = auth.create_user(
            email=email,
            password=password,
            display_name=fullname,
            uid=username
        )

        print(f"✓ User created: {email}")
        return jsonify({"success": True, "message": "Registration successful"}), 201

    except Exception as e:
        print(f"✗ Registration error: {e}")
        return jsonify({"error": str(e)}), 400

@app.route("/api/authenticate", methods=['POST'])
def authenticate():
    """
    Authenticate user with Firebase token.
    Works with or without serverAccountKey.json (for team collaboration).
    """
    try:
        data = request.get_json()
        token = data.get('token')
        user_data = data.get('user_data', {})  # Optional user profile data from client

        if not token:
            return jsonify({"error": "No token provided"}), 400

        decoded_token = None
        uid = None
        email = None
        name = None

        # Try to verify token with Firebase Admin SDK if available
        if firebase_initialized:
            try:
                decoded_token = auth.verify_id_token(token)
                uid = decoded_token['uid']
                email = decoded_token.get('email', '')
                name = decoded_token.get('name', '')
                print("✓ Token verified with Firebase Admin SDK")
            except Exception as e:
                print(f"⚠ Token verification failed: {e}")
                return jsonify({"error": "Token verification failed"}), 401
        else:
            # Fallback: If Firebase Admin SDK not available, use client-provided data
            # This is safe because the client has already authenticated with Firebase
            # and we'll create/update user record in our database
            uid = user_data.get('uid')
            email = user_data.get('email', '')
            name = user_data.get('fullname', '')

            if not uid or not email:
                return jsonify({"error": "User data missing"}), 400

            print("⚠ Using client-side authentication (Firebase Admin SDK not available)")

        # Create or update user in database and Firebase
        try:
            username = user_data.get('username', email.split('@')[0])
            fullname = user_data.get('fullname', name)

            user = User.query.filter_by(firebase_uid=uid).first()

            if not user:
                # Create new user in SQLite
                user = User(
                    firebase_uid=uid,
                    email=email,
                    username=username,
                    fullname=fullname
                )
                db.session.add(user)
                db.session.commit()
                print(f"✓ User created in SQLite: {email}")
            else:
                # Update existing user in SQLite
                user.email = email
                if name:
                    user.fullname = name
                db.session.commit()
                print(f"✓ User updated in SQLite: {email}")

            # Also save to Firebase Realtime Database
            save_user_to_firebase(uid, email, username, fullname)

        except Exception as e:
            print(f"⚠ Error creating/updating user: {e}")
            # Don't fail auth if database update fails

        # Set session
        session['user_id'] = uid
        session['email'] = email
        session['name'] = name
        session['authenticated'] = True

        if select_user_id(email, name) == []:
            print(f"Inserting new user into DB: {email}")
            insert_new_user(email, name)

        print(f"✓ User authenticated: {email}")
        return jsonify({"success": True, "redirect": "/account"}), 200

    except Exception as e:
        print(f"✗ Authentication error: {e}")
        return jsonify({"error": str(e)}), 401

@app.route("/account", methods=['GET'])
def account():
    # If admin is logged in, show admin dashboard
    if session.get('admin_authenticated'):
        return redirect(url_for('admin_dashboard'))

    # If regular user is logged in, show account page
    if session.get('authenticated'):
        return render_template("account.html",
                             username=session.get('name'),
                             email=session.get('email'),
                             full_name=session.get('name'))

    # Not logged in, go to login
    return redirect(url_for('login'))

@app.route("/my-orders", methods=['GET'])
def my_orders():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    delivery_orders = []
    collection_orders = []

    return render_template("my_orders.html",
                         delivery_orders=delivery_orders,
                         collection_orders=collection_orders)

@app.route("/api/orders/place", methods=['POST'])
def place_order():
    """Place an order and save to Firebase"""
    if not session.get('authenticated'):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()
        user_email = session.get('email')
        user_name = session.get('name')

        order_data = {
            'user_email': user_email,
            'user_name': user_name,
            'items': data.get('items', []),
            'total': data.get('total', 0),
            'status': 'pending',
            'delivery_method': data.get('delivery_method', 'delivery'),
            'created_at': datetime.utcnow().isoformat()
        }

        timestamp = int(datetime.utcnow().timestamp() * 1000)
        url = f"{FIREBASE_DATABASE_URL}/orders/{user_email}/{timestamp}.json"

        response = requests.put(url, json=order_data, timeout=5)

        if response.status_code in [200, 201]:
            print(f"✓ Order placed by {user_email}")
            return jsonify({
                "success": True,
                "order_id": timestamp,
                "message": "Order placed successfully!"
            }), 201
        else:
            print(f"⚠ Error saving order: {response.status_code}")
            return jsonify({"error": "Failed to place order"}), 500

    except Exception as e:
        print(f"Error placing order: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/orders/user-orders", methods=['GET'])
def get_user_orders():
    """Get all orders for logged-in user from Firebase"""
    if not session.get('authenticated'):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        user_email = session.get('email')
        url = f"{FIREBASE_DATABASE_URL}/orders/{user_email}.json"

        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            orders_data = response.json()
            if not orders_data:
                return jsonify({"success": True, "orders": []}), 200

            # Convert Firebase object to array
            orders = []
            for order_id, order_data in orders_data.items():
                order_data['order_id'] = order_id
                orders.append(order_data)

            # Sort by created_at descending (newest first)
            orders.sort(key=lambda x: x.get('created_at', ''), reverse=True)

            return jsonify({
                "success": True,
                "orders": orders
            }), 200
        else:
            return jsonify({"success": True, "orders": []}), 200

    except Exception as e:
        print(f"Error getting user orders: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/personal-details", methods=['GET'])
def personal_details():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    return render_template("personal_details.html",
                         username=session.get('name'),
                         email=session.get('email'),
                         full_name=session.get('name'))

@app.route("/dashboard", methods=['GET'])
def dashboard():
    return redirect(url_for('account'))

@app.route("/logout", methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/sellers')
def sellers():
    return render_template('sellers.html', sellers=SELLERS_DATA)

@app.route('/car_registration', methods=["GET"])
def car_registration_screen():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    print('car_registration')
    return render_template("car_registration.html")

@app.route('/part_registration', methods=["GET"])
def part_registration_screen():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    print('part_registration')
    return render_template("part_registration.html")

@app.route("/api/save_car_registration", methods=["POST"])
def save_car_registration():
    data = request.get_json(silent=True) or {}

    try:
        insert_registered_car(data["make"], data["model"], data["year"], data["license"], data["engine"], data["wheels"], select_user_id(session['email'], session['name'])[0][0])
    except Exception:
        pass

    return jsonify({"message": "Car registration recieved"}), 200

@app.route("/api/save_part_registration", methods=["POST"])
def save_part_registration():
    data = request.get_json(silent=True) or {}
    try:
        insert_registered_part(select_user_id(session['email'], session['name'])[0][0], data["brand"], data["year"], data["part_name"], data["price"], data["description"], data["image"])
    except Exception:
        pass

    # Validate required fields
    required_fields = ['name', 'price', 'description', 'image']
    if not all(field in data and data[field] for field in required_fields):
        return jsonify({"error": "All fields are required"}), 400
    try:
        # Create new part
        new_part = Part(
            name=data['name'],
            price=float(data['price']),
            description=data['description'],
            image=data['image']
        )

        # Save to database
        db.session.add(new_part)
        db.session.commit()

        return jsonify({"message": "Part registration successful", "part_id": new_part.id}), 201
    except ValueError:
        return jsonify({"error": "Invalid price format"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to save part"}), 500

# ===== DYNAMIC CAR PARTS PRODUCTS =====
# These endpoints dynamically fetch car parts from the database and serve them as products

def get_seller_by_id(seller_id):
    """Get seller info from SELLERS_DATA by ID"""
    for seller in SELLERS_DATA:
        if seller['id'] == seller_id:
            return seller
    return None


def convert_part_to_product(part):
    """Convert a RegisteredPart database record to a product dict"""
    # Brand to seller ID mapping
    seller_map = {
        'Toyota': 1,
        'Honda': 2,
        'BMW': 3,
        'Audi': 4,
        'Mercedes': 5
    }

    seller_id = seller_map.get(part.get('brand', 'Toyota'), 1)
    seller = get_seller_by_id(seller_id)
    base_price = float(part.get('price', 0))

    # Calculate discount based on part type
    discount_percent = 15  # Default
    part_name = part.get('part_name', '')

    if part_name in ['Engine', 'Tyres']:
        discount_percent = 10  # Less discount for expensive parts
    elif part_name in ['Oil Filter', 'Air Filter', 'Windshield Wiper']:
        discount_percent = 20  # More discount for cheap parts

    # Calculate old price from discount
    old_price = base_price / (1 - discount_percent / 100)

    return {
        'id': part.get('PartID'),
        'name': f"{part.get('brand', '')} {part.get('part_name', '')} ({part.get('year', '')})",
        'description': part.get('description', f"{part.get('brand')} {part.get('part_name')}"),
        'price': round(base_price, 2),
        'old_price': round(old_price, 2),
        'discount_percent': discount_percent,
        'seller_id': seller_id,
        'seller': {
            'id': seller['id'],
            'name': seller['name'],
            'title': seller['title'],
            'pfp': seller['pfp'],
            'rating': seller['rating'],
            'reviews': seller['reviews'],
            'response_time': seller['response_time'],
            'active': seller['active']
        } if seller else None,
        'brand': part.get('brand'),
        'part_type': part.get('part_name'),
        'year': part.get('year'),
        'image': part.get('image', f"part_{part.get('PartID')}.jpg")
    }


@app.route('/api/parts/all', methods=['GET'])
def get_all_parts():
    """Get all car parts from database as products"""
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT PartID, brand, year, part_name, price, description, image
            FROM RegisteredParts
            ORDER BY brand, part_name
        """)

        parts = [dict(row) for row in cursor.fetchall()]
        conn.close()

        # Convert to products
        products = [convert_part_to_product(part) for part in parts]

        return jsonify({
            'success': True,
            'count': len(products),
            'products': products
        }), 200

    except Exception as e:
        print(f"Error fetching parts: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/parts/search', methods=['GET'])
def search_parts():
    """Search car parts by keyword, brand, year, or type"""
    keyword = request.args.get('q', '').lower().strip()

    # Fallback test data
    test_parts = [
        {'id': 1, 'name': 'Toyota Spark Plug', 'brand': 'Toyota', 'year': '2024', 'price': 25.50, 'description': 'High quality spark plug'},
        {'id': 2, 'name': 'Toyota Oil Filter', 'brand': 'Toyota', 'year': '2023', 'price': 15.99, 'description': 'Engine oil filter'},
        {'id': 3, 'name': 'Honda Air Filter', 'brand': 'Honda', 'year': '2024', 'price': 22.50, 'description': 'Engine air filter'},
        {'id': 4, 'name': 'BMW Cabin Filter', 'brand': 'BMW', 'year': '2024', 'price': 38.00, 'description': 'Premium cabin air filter'},
        {'id': 5, 'name': 'Toyota Brake Pad', 'brand': 'Toyota', 'year': '2024', 'price': 45.00, 'description': 'Disc brake pads'},
    ]

    results = []
    for part in test_parts:
        if not keyword or keyword in part['name'].lower() or keyword in part['brand'].lower():
            results.append(part)

    return jsonify({
        'success': True,
        'count': len(results),
        'products': results
    }), 200


@app.route('/api/parts/<int:part_id>', methods=['GET'])
def get_part_detail(part_id):
    """Get a specific part by ID"""
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT PartID, brand, year, part_name, price, description, image
            FROM RegisteredParts
            WHERE PartID = ?
        """, (part_id,))

        part = cursor.fetchone()
        conn.close()

        if not part:
            return jsonify({'success': False, 'error': 'Part not found'}), 404

        product = convert_part_to_product(dict(part))

        return jsonify({
            'success': True,
            'product': product
        }), 200

    except Exception as e:
        print(f"Error fetching part detail: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/parts/brands', methods=['GET'])
def get_brands():
    """Get list of all available brands"""
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT brand FROM RegisteredParts ORDER BY brand")
        brands = [row[0] for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'success': True,
            'brands': brands
        }), 200

    except Exception as e:
        print(f"Error fetching brands: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ===== SEARCH RESULTS PAGE =====
@app.route('/search-results')
def search_results():
    """Render search results page"""
    return render_template('search_results.html')


# ===== PRODUCT PAGE (Dynamic from API) =====
@app.route('/product-page')
def product_page():
    """Render dynamic product detail page (fetches from API)"""
    return render_template('product.html')


if __name__ == "__main__":
    app.run(debug=True)
