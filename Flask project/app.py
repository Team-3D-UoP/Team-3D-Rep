import os
import random
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
from models import db, ProductReview, SellerReview, CartItem
from db_registrations import insert_registered_part

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///team3d.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

CORS(app)

# Create database tables
with app.app_context():
    db.create_all()

try:
    cred_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    print("Firebase initialized successfully")
except Exception as e:
    print(f"Firebase initialization error: {e}")


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
    """Get all reviews submitted by the current user (both product and seller reviews)"""
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    try:
        # Get all product reviews by user
        product_reviews = ProductReview.query.filter_by(
            user_id=session['user_id']
        ).order_by(ProductReview.created_at.desc()).all()

        # Get all seller reviews by user
        seller_reviews = SellerReview.query.filter_by(
            user_id=session['user_id']
        ).order_by(SellerReview.created_at.desc()).all()

        # Format product reviews with product details
        product_reviews_data = []
        for review in product_reviews:
            product = next((p for p in OFFER_PRODUCTS if p['id'] == review.product_id), None)
            if product:
                review_data = review.to_dict()
                review_data['type'] = 'product'
                review_data['item_name'] = product['name']
                review_data['item_id'] = review.product_id
                product_reviews_data.append(review_data)

        # Format seller reviews with seller details
        seller_reviews_data = []
        for review in seller_reviews:
            seller = next((s for s in SELLERS_DATA if s['id'] == review.seller_id), None)
            if seller:
                review_data = review.to_dict()
                review_data['type'] = 'seller'
                review_data['item_name'] = seller['name']
                review_data['item_id'] = review.seller_id
                seller_reviews_data.append(review_data)

        # Combine and sort by date
        all_reviews = product_reviews_data + seller_reviews_data
        all_reviews.sort(key=lambda x: x['created_at'], reverse=True)

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


@app.route("/api/calcTax", methods=['GET', 'POST'])
def calcTax():
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

@app.route("/login", methods=['GET'])
def login():
    return render_template("login_screen.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register_screen.html")

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

        print(f"User created: {email}")
        return jsonify({"success": True, "message": "Registration successful"}), 201

    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({"error": str(e)}), 400

@app.route("/api/authenticate", methods=['POST'])
def authenticate():
    try:
        data = request.get_json()
        token = data.get('token')

        if not token:
            return jsonify({"error": "No token provided"}), 400

        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        email = decoded_token.get('email', '')
        name = decoded_token.get('name', '')

        session['user_id'] = uid
        session['email'] = email
        session['name'] = name
        session['authenticated'] = True

        print(f"User authenticated: {email}")
        return jsonify({"success": True, "redirect": "/account"}), 200

    except Exception as e:
        print(f"Authentication error: {e}")
        return jsonify({"error": str(e), "details": "Check Firebase domain authorization"}), 401

@app.route("/account", methods=['GET'])
def account():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    return render_template("account.html",
                         username=session.get('name'),
                         email=session.get('email'),
                         full_name=session.get('name'))

@app.route("/my-orders", methods=['GET'])
def my_orders():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    delivery_orders = []
    collection_orders = []

    return render_template("my_orders.html",
                         delivery_orders=delivery_orders,
                         collection_orders=collection_orders)

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
     print('car_registration')
     return render_template("car_registration.html")

@app.route('/part_registration', methods=["GET"])
def part_registration_screen():
     print('part_registration')
     return render_template("part_registration.html")

@app.route("/api/save_car_registration", methods=["POST"])
def save_car_registration():
    data = request.get_json(silent=True) or {}

    # TODO: save to DB here
    try:
        #carId = Incremental
        print("make:", data["make"])
        print("model:", data["model"])
        print("year:", data["year"])
        print("license:", data["license"])
        print("engine:", data["engine"])
        print("wheels:", data["wheels"])
    except:
       pass

    return jsonify({"message": "Car registration recieved"}), 200

@app.route("/api/save_part_registration", methods=["POST"])
def save_part_registration():
    data = request.get_json(silent=True) or {}

    # TODO: GET USER ID FROM ACCOUNTS
    try:
        insert_registered_part(data["brand"], data["year"], data["part_name"], data["price"], data["description"], data["image"], user_id=None)
    except:
       pass

    return jsonify({"message": "Part registration recieved"}), 200

if __name__ == "__main__":
    app.run(debug=True)
