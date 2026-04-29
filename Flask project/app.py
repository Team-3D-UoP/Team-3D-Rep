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

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

CORS(app)

try:
    cred_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    print("Firebase initialized successfully")
except Exception as e:
    print(f"Firebase initialization error: {e}")


@app.route("/", methods=['GET'])
def home():
    # Assign sellers to each product
    products_with_sellers = []
    seller_index = 0
    shuffled_sellers = random.sample(SELLERS_DATA, len(SELLERS_DATA))
    
    for product in OFFER_PRODUCTS:
        product_with_seller = product.copy()
        # Cycle through sellers if we have more products than sellers
        product_with_seller['seller'] = shuffled_sellers[seller_index % len(shuffled_sellers)]
        products_with_sellers.append(product_with_seller)
        seller_index += 1
    
    return render_template("main_homepage.html", 
                         offer_products=products_with_sellers,
                         reviews=REVIEWS_DATA)

@app.route("/product/<int:product_id>", methods=['GET'])
def product_detail(product_id):
    # Find the product by ID
    product = next((p for p in OFFER_PRODUCTS if p['id'] == product_id), None)
    
    if not product:
        return "Product not found", 404
    
    # Get a random seller for this product
    seller = random.choice(SELLERS_DATA)
    product_with_seller = product.copy()
    product_with_seller['seller'] = seller
    
    return render_template("product_detail.html", product=product_with_seller)

@app.route("/product/<int:product_id>/review", methods=['POST'])
def submit_review(product_id):
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
    
        return jsonify({
            "success": True,
            "message": "Review submitted successfully"
        }), 200
        
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid data format"}), 400

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
        print("licence_plate:", data["licence_plate"])
        print("make:", data["make"])
        print("model:", data["model"])
        print("engine:", data["engine"])
        print("year:", data["year"])
        print("tyres:", data["tyres"])
    except:
       pass

    return jsonify({"message": "Car registration recieved"}), 200

@app.route("/api/save_part_registration", methods=["POST"])
def save_part_registration():
    data = request.get_json(silent=True) or {}

    # TODO: save to DB here
    try:
        print("name:", data["name"])
        print("price:", data["price"])
        print("description:", data["description"])
        print("image:", data["image"])
    except:
       pass

    return jsonify({"message": "Part registration recieved"}), 200

if __name__ == "__main__":
    app.run(debug=True)
