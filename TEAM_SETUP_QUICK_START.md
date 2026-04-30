# Team 3D - Quick Start Setup Guide

**Good news:** You don't need any secret keys to run this app! 🎉

---

## One-Time Setup (5 minutes)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd Team-3D-Rep
```

### Step 2: Install Python Dependencies
```bash
pip install flask flask-sqlalchemy flask-cors python-dotenv pillow firebase-admin
```

### Step 3: Run the App
```bash
cd "Flask project"
python app.py
```

### Step 4: Open in Browser
```
http://localhost:5000
```

---

## Done! You're Ready to Go ✅

The app will:
- ✓ Create a local SQLite database (`team3d.db`)
- ✓ Set up user tables automatically
- ✓ Allow login/register using Firebase (public config in code)
- ✓ Store user profiles locally

---

## Features You Can Use

### Login & Register
- Email + password signup
- Login to your account
- Google login available

### Shopping Cart
- Add products to cart
- View cart with quantities
- Remove items
- See cart count in header

### Reviews
- Leave product reviews with ratings
- Leave seller reviews with ratings
- See your reviews in account page
- See reviews on product/seller pages

### Account Dashboard
- View your profile
- See all your reviews
- See your orders

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'firebase_admin'"
```bash
pip install firebase-admin
```

### "Database is locked"
- Close other instances of the app running
- Delete `instance/team3d.db` and run again

### Can't login/register
1. Check email is correct format
2. Password must be 6+ characters
3. Check browser console for errors (F12)

### Cart not showing count
- Refresh page (F5)
- Make sure you're logged in

---

## What You Need to Know

**You DON'T need:**
- ❌ `serviceAccountKey.json` (secret key)
- ❌ Firebase credentials
- ❌ Environment variables for auth

**The app has:**
- ✅ Public Firebase config (safe to share)
- ✅ Client-side authentication
- ✅ Local database for user profiles
- ✅ Session management

---

## Where to Find Things

```
Flask project/
├── app.py (main Flask app)
├── models.py (database models: User, ProductReview, SellerReview, CartItem)
├── templates/ (all HTML pages)
│   ├── login_screen.html (login with Firebase)
│   ├── register_screen.html (signup with Firebase)
│   ├── main_homepage.html (homepage)
│   ├── account.html (user dashboard)
│   └── ...
├── data/ (product/seller data)
└── team3d.db (SQLite database - created on first run)
```

---

## Development Tips

### Run with Debug Mode
```bash
export FLASK_DEBUG=1  # Linux/Mac
set FLASK_DEBUG=1     # Windows

python app.py
```

### Clear Database
```bash
rm team3d.db
python app.py
```

### Check Logs
- Look at terminal where `python app.py` runs
- See authentication status, database operations, etc.

---

## Common Questions

**Q: Why don't I need serviceAccountKey.json?**
A: The app uses client-side Firebase authentication. You log in directly with Firebase in your browser, then the server just stores your profile.

**Q: Is my password safe?**
A: Yes! Passwords go directly to Firebase, not through this server. The server never sees your password.

**Q: Where are my reviews stored?**
A: In the local SQLite database (`team3d.db`). They're stored on your computer.

**Q: Can I sync data between computers?**
A: Not yet - each copy has its own database. For team syncing, switch from SQLite to a shared database (PostgreSQL, MySQL, etc.)

**Q: Does localhost work without internet?**
A: No, you need internet for Firebase authentication. Everything else works offline.

---

## Next Steps

1. ✅ Run the app
2. ✅ Test login/register
3. ✅ Try adding products to cart
4. ✅ Leave a review
5. ✅ Check your account page

---

## Still Having Issues?

Check the main guide: `FIREBASE_SETUP_GUIDE.md`

Or ask the team lead! 👋
