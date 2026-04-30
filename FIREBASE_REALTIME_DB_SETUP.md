# Firebase Realtime Database Setup

## ✅ What's Done

Your app is now connected to Firebase Realtime Database! When users:
- **Register/Login** → User profile saved to Firebase
- **Leave a review** → Review saved to Firebase  
- **Add to cart** → Cart item saved to Firebase

---

## 🔧 Set Up Database Rules

Your database is currently in "Test mode" (anyone can read/write). For security, let's set proper rules.

### Step 1: Open Firebase Console

1. Go to https://console.firebase.google.com
2. Select your "team-3d-2ad7c" project
3. Click **"Realtime Database"** in left sidebar
4. Click the **"Rules"** tab

### Step 2: Replace Rules with This

Delete everything and paste:

```json
{
  "rules": {
    "users": {
      "$uid": {
        ".read": "auth.uid === $uid || root.child('users').child($uid).exists()",
        ".write": "auth.uid === $uid"
      }
    },
    "reviews": {
      ".read": true,
      "product": {
        "$product_id": {
          ".write": "auth != null"
        }
      },
      "seller": {
        "$seller_id": {
          ".write": "auth != null"
        }
      }
    },
    "carts": {
      "$uid": {
        ".read": "auth.uid === $uid",
        ".write": "auth.uid === $uid"
      }
    }
  }
}
```

### Step 3: Publish Rules

Click **"Publish"** button

---

## 📊 Database Structure

Your Firebase Realtime Database now has this structure:

```
root/
├── users/
│   └── {firebase_uid}/
│       ├── email: "user@example.com"
│       ├── username: "john_doe"
│       ├── fullname: "John Doe"
│       ├── created_at: "2026-04-30T..."
│       └── updated_at: "2026-04-30T..."
│
├── reviews/
│   ├── product/
│   │   └── {product_id}/
│   │       └── {user_id}/
│   │           ├── item_id: 1
│   │           ├── user_id: "abc123"
│   │           ├── user_email: "user@example.com"
│   │           ├── user_name: "John Doe"
│   │           ├── rating: 5
│   │           ├── review_text: "Great product!"
│   │           └── created_at: "2026-04-30T..."
│   │
│   └── seller/
│       └── {seller_id}/
│           └── {user_id}/
│               ├── item_id: 3
│               ├── rating: 4
│               ├── review_text: "Good service"
│               └── created_at: "2026-04-30T..."
│
└── carts/
    └── {firebase_uid}/
        └── {product_id}/
            ├── product_id: 1
            ├── quantity: 2
            └── updated_at: "2026-04-30T..."
```

---

## 🚀 Test It Out

1. **Stop your app** (Ctrl+C in terminal)
2. **Run app again**: `python app.py`
3. **Register a new user** → Check Firebase Console
   - Go to Realtime Database → Data tab
   - You should see the user in `users/{uid}`
4. **Add product to cart** → Check `carts/{uid}/{product_id}`
5. **Leave a review** → Check `reviews/seller/{seller_id}/{uid}`

---

## ✨ Benefits Now

✅ **Team Collaboration**: All team members see same data  
✅ **Cloud Backup**: Data backed up by Firebase  
✅ **Real-time Sync**: Changes instant across all users  
✅ **No Local Files**: No SQLite files to worry about  
✅ **Scalable**: Grows with your app  

---

## 🔍 View Your Data

**In Firebase Console:**
1. Click **"Realtime Database"**
2. Click **"Data"** tab
3. Browse the structure
4. Click any value to see details

---

## 📝 Notes

- SQLite database (`team3d.db`) still works in parallel
- Firebase is the "cloud mirror" of your data
- Both sources stay in sync automatically
- Team members can see all shared data

---

## Next Steps (Optional)

### Switch Completely to Firebase (Remove SQLite)
If you want to use ONLY Firebase (no SQLite):
1. Remove `from models import db, ...`
2. Remove all `db.session` calls
3. Read/write only from Firebase functions

This is more complex, so keep SQLite for now!

### Add More Firebase Features
- Real-time product price updates
- Live chat using Firebase
- Push notifications
- File uploads

---

## Troubleshooting

### "Error saving to Firebase"
- Check Firebase is initialized correctly
- Verify database URL in app.py
- Check security rules allow writes

### Data not appearing in Firebase Console
- Refresh browser (F5)
- Make sure user is logged in
- Check terminal for error messages

### "Permission denied" errors
- Database rules might be too restrictive
- Check rules match the structure above
- Ensure user is authenticated

---

## Database URL Used

```
https://team-3d-default-rtdb.europe-west1.firebasedatabase.app
```

This is already configured in your app.py!
