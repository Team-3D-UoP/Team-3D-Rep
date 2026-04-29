# Shopping Cart Testing Guide

## Step-by-Step Testing Instructions

### Setup
1. Make sure Flask app is running: `python app.py`
2. Ensure you have `flask-sqlalchemy` installed: `pip install flask-sqlalchemy`

### Test Scenario 1: Add Item to Cart (Logged Out)
**Expected**: User redirected to login
1. Go to http://localhost:5000/ (homepage)
2. Click on any product
3. Click "Add to Cart"
4. ✅ Should see: "Please log in to add items to your cart"
5. ✅ Should be redirected to login page

### Test Scenario 2: Add Item to Cart (Logged In)
**Expected**: Item successfully added
1. Register/Login at http://localhost:5000/register
2. Go to http://localhost:5000/product/1 (Pressure Washer)
3. Click "Add to Cart"
4. ✅ Should see: "Item added to cart successfully!"
5. Click "Add to Cart" again for same item
6. ✅ Should update quantity in database

### Test Scenario 3: View Shopping Cart
**Expected**: See all items with images and prices
1. After adding items, go to http://localhost:5000/cart
2. ✅ Should see:
   - Product image
   - Product name (clickable link)
   - Product price
   - Quantity controls
   - Remove button
   - Order summary on the right
   - Subtotal, Shipping (£5.00), Total

### Test Scenario 4: Update Quantities
**Expected**: Quantities update and total recalculates
1. On cart page, find an item
2. Click the "-" button
3. ✅ Quantity should decrease
4. ✅ Total should update
5. Click "+" button
6. ✅ Quantity should increase
7. Or enter a number in quantity field and press Enter
8. ✅ Cart updates immediately

### Test Scenario 5: Remove Item from Cart
**Expected**: Item removed, cart updates
1. On cart page, click "Remove" button on an item
2. ✅ Should see confirmation dialog: "Are you sure you want to remove this item?"
3. Click "OK"
4. ✅ Item should disappear
5. ✅ Cart total should update
6. If all items removed: ✅ Should see "Your cart is empty" message

### Test Scenario 6: Empty Cart
**Expected**: Special message displayed
1. Add item to cart
2. Remove all items
3. ✅ Should see:
   - Shopping bag emoji 🛒
   - "Your cart is empty" message
   - "Continue Shopping" button (link to homepage)

### Test Scenario 7: Continue Shopping
**Expected**: Return to homepage
1. On empty cart page, click "Continue Shopping"
2. ✅ Should go back to homepage
3. Or on cart page with items, click "Continue Shopping" button
4. ✅ Should go to homepage but cart items persist

### Test Scenario 8: Cart Persistence
**Expected**: Items stay after page refresh
1. Add items to cart
2. Go to http://localhost:5000/cart
3. Note the items and total
4. Refresh page (F5 or Cmd+R)
5. ✅ Same items should still be there
6. ✅ Quantities and total should be unchanged

### Test Scenario 9: Multiple Products
**Expected**: Can add different products
1. Add Pressure Washer to cart
2. Go to http://localhost:5000/product/2 (different product)
3. Add Car Cleaning Kit to cart
4. Go to http://localhost:5000/cart
5. ✅ Should see both items with different images and prices
6. ✅ Total should be sum of both items + shipping

### Test Scenario 10: Price Calculation
**Expected**: Prices calculate correctly
1. Add item with price £49.99, quantity 2
2. ✅ Line total should be £99.98
3. Add another item with price £29.99, quantity 1
4. ✅ Subtotal = £99.98 + £29.99 = £129.97
5. ✅ Shipping = £5.00
6. ✅ Total = £134.97

## Browser Console Debugging

To check network requests and JavaScript errors:

1. Open Browser DevTools (F12 or Cmd+Option+I)
2. Go to **Network** tab
3. Perform cart actions
4. ✅ Should see successful requests to:
   - POST /api/cart/add (201 Created or 200 OK)
   - GET /api/cart (200 OK)
   - PUT /api/cart/item/<id> (200 OK)
   - DELETE /api/cart/item/<id> (200 OK)

4. Go to **Console** tab
5. ✅ Should not see any red error messages
6. You might see console.log messages for debugging

## API Testing with curl (Optional)

```bash
# Add item to cart (requires valid session)
curl -X POST http://localhost:5000/api/cart/add \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 1}'

# Get cart items
curl http://localhost:5000/api/cart

# Update quantity
curl -X PUT http://localhost:5000/api/cart/item/1 \
  -H "Content-Type: application/json" \
  -d '{"quantity": 5}'

# Remove item
curl -X DELETE http://localhost:5000/api/cart/item/1
```

## Common Issues & Solutions

### Issue: "User not logged in" error
**Solution**: Make sure you're logged in before adding items to cart

### Issue: Cart page shows "Error loading cart"
**Solution**: 
1. Check browser console (F12) for errors
2. Make sure CartItem table exists in database
3. Try refreshing the page
4. Check Flask console for error messages

### Issue: Quantity doesn't update
**Solution**:
1. Make sure you're entering a valid number (1 or higher)
2. Check network tab to see if PUT request is succeeding
3. Try refreshing page

### Issue: Items disappear after logout/login
**Solution**: This is expected behavior - each user has separate cart items based on user_id

### Issue: Total price wrong
**Solution**:
1. Shipping is always £5.00 per order (if items in cart)
2. Each product has a current_price in the data
3. Subtotal = sum of (product_price × quantity) for all items
4. Total = Subtotal + £5.00

## What to Check in Database

```python
# In Python shell with Flask context:
from app import app, db
from models import CartItem

with app.app_context():
    # See all cart items
    items = CartItem.query.all()
    for item in items:
        print(f"User: {item.user_id}, Product: {item.product_id}, Qty: {item.quantity}")
    
    # See items for specific user
    user_items = CartItem.query.filter_by(user_id='your_user_id').all()
```

## Performance Notes

- Cart loads via AJAX (async) - doesn't require page reload
- Each action updates database immediately
- Calculations happen in JavaScript for UI responsiveness
- Prices pulled from OFFER_PRODUCTS data structure

---

**If everything passes these tests, your shopping cart system is working correctly!** ✅
