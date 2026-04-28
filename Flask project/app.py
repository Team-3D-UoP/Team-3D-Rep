from flask import Flask, request, jsonify, render_template, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'SECRET_KEY'

def get_footer_data():
    return {
        "footer_columns": [
            {"title": "How to Shop", "links": [
                {"label": "Easy Ways to Shop", "url": "#"},
                {"label": "Our App", "url": "#"},
                {"label": "Car Parts Online", "url": "#"},
                {"label": "Store Locator", "url": "#"},
                {"label": "Brands", "url": "#"},
                {"label": "Safe Shopping", "url": "#"},
                {"label": "Great Value, Always", "url": "#"}
            ]},
            {"title": "Customer Services", "links": [
                {"label": "My Account", "url": "#"},
                {"label": "Track Your Order", "url": "#"},
                {"label": "Delivery Information", "url": "#"},
                {"label": "Returns & Refunds", "url": "#"},
                {"label": "Warranty", "url": "#"},
                {"label": "Help Centre", "url": "#"},
                {"label": "Product Recall", "url": "#"},
                {"label": "Contact Us", "url": "#"}
            ]},
            {"title": "Legal Notices", "links": [
                {"label": "Privacy Notice", "url": "#"},
                {"label": "Security Policy", "url": "#"},
                {"label": "Cookie Policy", "url": "#"},
                {"label": "Terms & Conditions", "url": "#"}
            ]},
            {"title": "About Us", "links": [
                {"label": "Corporate Web Site", "url": "#"},
                {"label": "CSR", "url": "#"},
                {"label": "Careers", "url": "#"},
                {"label": "Newsletter Sign up", "url": "#"}
            ]},
            {"title": "Feedback", "links": [
                {"label": "Send Feedback", "url": "#"}
            ]}
        ],
        "payment_icons": ["💳 Visa", "💳 Mastercard", "💳 Amex", "💳 PayPal"],
        "security_icons": ["🔒 SSL", "🛡️ Fraud protection", "✅ Verified"],
        "paypal_text": "REPRESENTATIVE EXAMPLE: PURCHASE RATE 23.9% P.A. (VARIABLE)",
        "footer_bottom_text": "LKQ Group (UK) Limited T/A LKQ Euro Car Parts - terms, privacy and regulatory information."
    }

@app.route("/", methods=['GET'])
def home():
    print('home')
    footer_ctx = get_footer_data()
    return render_template("main_homepage.html", **footer_ctx)

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
     footer_ctx = get_footer_data()
     return render_template("confirm.html", **footer_ctx)

  
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


if __name__ == "__main__":
    app.run(debug=True)
