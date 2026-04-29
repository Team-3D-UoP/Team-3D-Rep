import os
import random
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from data.products import OFFER_PRODUCTS
from data.sellers import SELLERS_DATA
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

reviews_data = [
    {
        'name': 'John Mitchell',
        'time': '2 days ago',
        'rating': 5,
        'text': 'Great quality parts and fast delivery. Very satisfied with my purchase and would recommend to others.'
    },
    {
        'name': 'Sarah Johnson',
        'time': '5 days ago',
        'rating': 5,
        'text': 'Excellent customer service. The team helped me find exactly what I needed. Highly recommended!'
    },
    {
        'name': 'Mark Thompson',
        'time': '1 week ago',
        'rating': 4,
        'text': 'Good products and reasonable prices. Shipping took a bit longer than expected but overall satisfied.'
    },
    {
        'name': 'Emma Wilson',
        'time': '1 week ago',
        'rating': 5,
        'text': 'Best prices I\'ve found online for car parts. Fast shipping and items arrived in perfect condition.'
    },
    {
        'name': 'David Chen',
        'time': '2 weeks ago',
        'rating': 5,
        'text': 'Fantastic selection and competitive pricing. Will definitely order again. Highly recommended!'
    },
    {
        'name': 'Lisa Anderson',
        'time': '2 weeks ago',
        'rating': 5,
        'text': 'Excellent product quality and reliable service. Customer support was very helpful when I had questions.'
    },
    {
        'name': 'Robert Taylor',
        'time': '3 weeks ago',
        'rating': 4,
        'text': 'Good experience overall. Products arrived quickly and are exactly as described. Minor packaging issue.'
    },
    {
        'name': 'Jennifer Brown',
        'time': '3 weeks ago',
        'rating': 5,
        'text': 'Amazing prices and quick delivery. Best car parts supplier I\'ve used. Five stars all the way!'
    }
]

@app.route("/", methods=['GET'])
def home():
    # Assign sellers to each product
    products_with_sellers = []
    seller_index = 0
    shuffled_sellers = random.sample(sellers_data, len(sellers_data))
    
    for product in OFFER_PRODUCTS:
        product_with_seller = product.copy()
        # Cycle through sellers if we have more products than sellers
        product_with_seller['seller'] = shuffled_sellers[seller_index % len(shuffled_sellers)]
        products_with_sellers.append(product_with_seller)
        seller_index += 1
    
    return render_template("main_homepage.html", 
                         offer_products=products_with_sellers,
                         reviews=reviews_data)

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
    return render_template('sellers.html', sellers=sellers_data)

if __name__ == "__main__":
    app.run(debug=True)
