from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from data.products import OFFER_PRODUCTS
from io import BytesIO
from PIL import Image, ImageDraw
import base64

app = Flask(__name__)
app.secret_key = 'SECRET_KEY'

@app.route("/", methods=['GET'])
def home():
    print('home')
    return render_template("main_homepage.html", offer_products=OFFER_PRODUCTS)

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
     print('confirm')
     return render_template("confirm.html")

  
@app.route("/api/saveTax", methods=["POST"])
def save_incomes():
  data = request.get_json(silent=True)
  
  print('save')

  try:
    a = float(data["a"])
    b = float(data["b"])
    
    print(a, b)
    # this is where we save the inputs in a db
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
    """Generate placeholder images for products"""
    img = Image.new('RGB', (120, 120), color='#f0f0f0')
    draw = ImageDraw.Draw(img)
    
    # Add text to image
    draw.text((10, 50), part_name[:15], fill='#003d7a')
    
    # Convert to base64
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode()
    
    return f"data:image/png;base64,{img_base64}"

@app.route("/login", methods=['GET'])
def login():
    print('login')
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)
