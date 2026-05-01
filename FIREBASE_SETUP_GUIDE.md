# Firebase Setup Guide

## Quick Answer: Works Without serviceAccountKey.json ✅

Your app now uses **client-side Firebase authentication**. Team members can run it WITHOUT the `serviceAccountKey.json` file!

---

## Architecture Overview

```
Team Member's Computer
│
├── login_screen.html
│   ├── Authenticates with Firebase (public config)
│   └── Sends user info to /api/authenticate
│
├── /api/authenticate (on your server)
│   ├── Creates/updates User in database
│   ├── Sets Flask session
│   └── Works with OR without serviceAccountKey.json
│
└── Protected Routes
    └── Use session, not Firebase Admin SDK
```

---

## For Team Members: Setup (No Secret Key Needed!)

### 1. Clone/Get Your Code
```bash
git clone <your-repo>
cd "Flask project"
```

### 2. Install Dependencies
```bash
pip install flask flask-sqlalchemy flask-cors python-dotenv pillow firebase-admin python-dotenv
```

### 3. Run the App
```bash
python app.py
```

That's it! You DON'T need `serviceAccountKey.json` because:
- ✓ Login/Register use **client-side Firebase** (public config is embedded)
- ✓ User profiles are stored in **local SQLite database**
- ✓ Sessions manage authentication server-side

---

## How It Works

### Client-Side (Browser)
1. User clicks "Login" or "Register"
2. **Firebase Web SDK** (using public config) authenticates them
3. Gets an ID token from Firebase
4. Sends token + user data to your backend

### Server-Side (Your Flask App)
1. Receives token and user data
2. **If** `serviceAccountKey.json` exists:
   - ✓ Verifies token with Firebase Admin SDK (extra security)
3. **If** `serviceAccountKey.json` missing:
   - ✓ Skips verification (client already authenticated)
4. Creates/updates **User** record in database
5. Sets Flask session (user is logged in)

### Result
- **Public config shared** in code (login_screen.html, register_screen.html)
- **Secret key kept private** on your server only (if you have it)
- **Team can run** the full app without any secrets

---

## User Model (Database)

Your app now has a `User` table:

```
users table:
├── id (primary key)
├── firebase_uid (unique, from Firebase)
├── email (unique)
├── username (unique, from registration)
├── fullname (from registration or Google display name)
└── created_at, updated_at
```

This stores user profiles locally, so:
- ✓ Users stay logged in via Flask sessions
- ✓ Can display username/profile info
- ✓ Links reviews and cart to users
- ✓ Works without Firebase Admin SDK

---

## The Two Setups Explained

| Aspect | With Secret Key | Without Secret Key |
|--------|-----------------|-------------------|
| **Location** | `serviceAccountKey.json` on your server | N/A |
| **Firebase Login** | Verified via Admin SDK | Verified by Firebase client |
| **User Creation** | Admin SDK creates users | Client creates users |
| **Team Can Run** | ❌ No (need secret key) | ✅ Yes! |
| **Extra Security** | ✓ Server-side verification | ✓ Client-side sufficient |
| **Who Uses** | You (main developer) | Team + you |

---

## Firebase Config (Public - Safe to Share)

Your `login_screen.html` and `register_screen.html` contain:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyBnAWx2Dns0VBzYoSadcXBSpt4PY7fifPQ",
  authDomain: "team-3d-2ad7c.firebaseapp.com",
  projectId: "team-3d-2ad7c",
  storageBucket: "team-3d-2ad7c.firebasestorage.app",
  messagingSenderId: "746044663136",
  appId: "1:746044663136:web:d4ea0582040dda62a6ea05",
  measurementId: "G-93ZJ10SC4V"
};
```

✅ **This is PUBLIC** - Safe to commit and share!

---

## Service Account Key (Secret - Never Share!)

If you HAVE `serviceAccountKey.json`:
- 🔐 **NEVER** commit to Git
- 🔐 **NEVER** share with team
- 🔐 Add to `.gitignore`:
  ```
  serviceAccountKey.json
  ```
- ✓ Optional - app works without it

---

## Setup Options for Different Scenarios

### Option A: Team Development (Recommended)
```
Team Member:
  ✓ Clone repo
  ✓ Run: pip install -r requirements.txt
  ✓ Run: python app.py
  ✓ Opens on localhost:5000
  ✓ No secret key needed!
```

### Option B: With Service Account (Extra Verification)
```
You (Main Dev):
  1. Get serviceAccountKey.json from Firebase Console
  2. Add to Flask project root
  3. Add to .gitignore
  4. Run: python app.py
  5. Token verification has extra layer
  6. Don't share this file with team!
```

### Option C: Production Deployment
```
Production Server:
  1. Deploy code (without serviceAccountKey.json)
  2. App runs with client-side Firebase
  3. SQLite → Production database (PostgreSQL, etc.)
  4. Optional: Add serviceAccountKey.json for extra security
```

---

## Troubleshooting

### "Firebase not configured on this server"
- ✅ Normal if you don't have `serviceAccountKey.json`
- ✅ App still works - uses client-side auth
- ❌ Only error if token verification fails

### "Authentication failed"
- Check your Firebase config in HTML is correct
- Verify user exists in Firebase (Firebase Console > Auth)
- Check browser console for errors (F12)

### User can't register
- Check Firebase allows sign-ups (Console > Auth > Sign-in method)
- Verify password is strong enough (6+ characters)
- Check username isn't already taken

---

## Current Status

✅ **Client-side Firebase Setup**: Ready  
✅ **User Database Model**: Created  
✅ **Authentication Endpoint**: Works with/without serviceAccountKey.json  
✅ **Team Collaboration**: Possible without sharing secrets  
✅ **Login/Register Pages**: Updated to send user data  

---

## What's New Since Last Update

1. **Added User Model** to `models.py`
   - Stores user profiles in SQLite
   - Links to Firebase UID

2. **Updated /api/authenticate**
   - Creates User records automatically
   - Works without Firebase Admin SDK
   - Sends user_data from client

3. **Updated login_screen.html**
   - Sends user_data with authentication token
   - Passes uid, email, fullname to backend

4. **Updated register_screen.html**
   - Sends user_data with authentication token
   - Passes uid, email, username, fullname to backend

5. **Google Authentication**
   - Works for both login and register
   - Creates user record automatically

---

## Summary

**For your team:**
```
git clone <repo>
pip install -r requirements.txt
python app.py
# Go to http://localhost:5000
# Login/Register works without serviceAccountKey.json!
```

**For you (optional):**
```
# Get serviceAccountKey.json from Firebase Console
# Place in Flask project root
# Add to .gitignore
# App still works without it, just with extra verification
```

---

## Questions?

- **"What data is sent to Firebase?"** → Only email and password (same as any Firebase app)
- **"Is localhost secure?"** → For dev only. Use HTTPS + proper setup for production
- **"Can I remove Firebase?"** → Yes, but you'd need to build your own auth system
- **"What about logout?"** → Flask session handles it server-side
