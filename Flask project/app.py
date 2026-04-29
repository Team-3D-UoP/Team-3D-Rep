import os
import random
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from data.products import OFFER_PRODUCTS
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

sellers_data = [
    {
        'name': 'Alex Mitchell',
        'title': '3D Printing Expert',
        'pfp': 'A',
        'rating': 4.9,
        'reviews': 287,
        'joined': 'Jan 15, 2022',
        'products_sold': 542,
        'response_time': '2 hours',
        'positive_feedback': 98,
        'active': True
    },
    {
        'name': 'Bella Chen',
        'title': 'CAD Designer',
        'pfp': 'B',
        'rating': 4.7,
        'reviews': 156,
        'joined': 'Mar 22, 2022',
        'products_sold': 389,
        'response_time': '4 hours',
        'positive_feedback': 96,
        'active': True
    },
    {
        'name': 'Carlos Rodriguez',
        'title': 'Prototype Builder',
        'pfp': 'C',
        'rating': 5.0,
        'reviews': 203,
        'joined': 'Feb 08, 2022',
        'products_sold': 478,
        'response_time': '1 hour',
        'positive_feedback': 99,
        'active': True
    },
    {
        'name': 'Diana Thompson',
        'title': 'Model Creator',
        'pfp': 'D',
        'rating': 4.6,
        'reviews': 134,
        'joined': 'May 10, 2023',
        'products_sold': 267,
        'response_time': '3 hours',
        'positive_feedback': 94,
        'active': True
    },
    {
        'name': 'Eric Kim',
        'title': 'Tech Specialist',
        'pfp': 'E',
        'rating': 4.8,
        'reviews': 298,
        'joined': 'Aug 30, 2021',
        'products_sold': 612,
        'response_time': '1 hour',
        'positive_feedback': 97,
        'active': True
    },
    {
        'name': 'Fiona Walsh',
        'title': 'Quality Assurance',
        'pfp': 'F',
        'rating': 3.8,
        'reviews': 92,
        'joined': 'Nov 05, 2023',
        'products_sold': 145,
        'response_time': '8 hours',
        'positive_feedback': 88,
        'active': False
    },
    {
        'name': 'Gabriel Santos',
        'title': 'Custom Fabrication',
        'pfp': 'G',
        'rating': 4.9,
        'reviews': 215,
        'joined': 'Dec 12, 2021',
        'products_sold': 531,
        'response_time': '2 hours',
        'positive_feedback': 98,
        'active': True
    },
    {
        'name': 'Hannah Price',
        'title': 'Consulting Expert',
        'pfp': 'H',
        'rating': 4.5,
        'reviews': 178,
        'joined': 'Apr 18, 2022',
        'products_sold': 423,
        'response_time': '5 hours',
        'positive_feedback': 93,
        'active': True
    }
]

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
    random_seller = random.choice(sellers_data)
    remaining_sellers = [s for s in sellers_data if s != random_seller]
    random_secondary_seller = random.choice(remaining_sellers)
    remaining_sellers_two = [s for s in remaining_sellers if s != random_secondary_seller]
    random_tertiary_seller = random.choice(remaining_sellers_two)
    
    return render_template("main_homepage.html", 
                         offer_products=OFFER_PRODUCTS, 
                         featured_seller=random_seller, 
                         secondary_seller=random_secondary_seller,
                         tertiary_seller=random_tertiary_seller,
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
