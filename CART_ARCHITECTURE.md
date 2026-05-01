# Shopping Cart System Architecture

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐      ┌──────────────────┐                 │
│  │  Product Detail  │      │  Shopping Cart   │                 │
│  │     Page         │      │      Page        │                 │
│  │ (product_detail  │      │   (cart.html)    │                 │
│  │    .html)        │      │                  │                 │
│  └────────┬─────────┘      └─────────┬────────┘                 │
│           │                          │                           │
│  ┌────────▼──────────────┐  ┌──────────────────┐                │
│  │ "Add to Cart" Button  │  │  Cart Controls   │                │
│  │  Click Handler        │  │ (quantity +/-)   │                │
│  │  - Check login        │  │  Remove buttons  │                │
│  │  - POST to API        │  │                  │                │
│  └────────┬──────────────┘  └────────┬─────────┘                │
│           │                          │                           │
│           ▼                          ▼                           │
│  ┌─────────────────────────────────────┐                        │
│  │        AJAX Requests                │                        │
│  │  (JavaScript fetch() calls)         │                        │
│  │                                     │                        │
│  │  POST   /api/cart/add               │                        │
│  │  GET    /api/cart                   │                        │
│  │  PUT    /api/cart/item/<id>         │                        │
│  │  DELETE /api/cart/item/<id>         │                        │
│  └────────────┬────────────────────────┘                        │
│               │                                                  │
└───────────────┼──────────────────────────────────────────────────┘
                │
                │ HTTP Requests
                │
┌───────────────▼──────────────────────────────────────────────────┐
│                    Flask Backend (app.py)                        │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │               Route Handlers                                 │ │
│  │                                                              │ │
│  │  @app.route("/api/cart/add", methods=['POST'])             │ │
│  │  def add_to_cart():                                         │ │
│  │    - Validate user is logged in                            │ │
│  │    - Check product exists in OFFER_PRODUCTS                │ │
│  │    - Create or update CartItem in database                 │ │
│  │    - Return JSON response                                  │ │
│  │                                                              │ │
│  │  @app.route("/api/cart", methods=['GET'])                  │ │
│  │  def get_cart():                                           │ │
│  │    - Fetch all CartItem for current user                   │ │
│  │    - Join with OFFER_PRODUCTS for details                  │ │
│  │    - Calculate totals                                      │ │
│  │    - Return JSON with all cart data                        │ │
│  │                                                              │ │
│  │  @app.route("/api/cart/item/<id>", methods=['PUT'])        │ │
│  │  def update_cart_item():                                   │ │
│  │    - Validate quantity >= 1                                │ │
│  │    - Update CartItem quantity                              │ │
│  │    - Return success response                               │ │
│  │                                                              │ │
│  │  @app.route("/api/cart/item/<id>", methods=['DELETE'])     │ │
│  │  def remove_from_cart():                                   │ │
│  │    - Delete CartItem from database                         │ │
│  │    - Return success response                               │ │
│  │                                                              │ │
│  │  @app.route("/cart", methods=['GET'])                      │ │
│  │  def view_cart():                                          │ │
│  │    - Render cart.html template                            │ │
│  │    - Return HTML page                                      │ │
│  │                                                              │ │
│  └──────────────────┬────────────────────────────────────────┘ │
│                     │                                            │
│                     ▼                                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Database Layer (SQLAlchemy)                  │  │
│  │                                                            │  │
│  │  CartItem Model:                                          │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ id (Integer, Primary Key)                          │  │  │
│  │  │ user_id (String, Indexed, Foreign Key to User)    │  │  │
│  │  │ product_id (Integer, Foreign Key to Product)      │  │  │
│  │  │ quantity (Integer, Default: 1)                     │  │  │
│  │  │ created_at (DateTime)                              │  │  │
│  │  │ updated_at (DateTime)                              │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                            │  │
│  │  Database: SQLite (team3d.db) or PostgreSQL              │  │
│  │  Table: cart_items                                        │  │
│  │                                                            │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

## Data Flow for Each Operation

### 1. Add Item to Cart
```
User clicks "Add to Cart"
    ↓
JavaScript checks: Is user logged in?
    ├─→ NO: Redirect to login
    └─→ YES: Continue
    ↓
JavaScript sends POST /api/cart/add
    ↓
Flask handler:
    1. Verify user_id in session
    2. Get product_id from request
    3. Check product exists in OFFER_PRODUCTS
    4. Query: CartItem.filter_by(user_id, product_id)
       ├─→ EXISTS: Update quantity += 1
       └─→ NEW: Create CartItem
    5. db.session.commit()
    6. Return {success: True}
    ↓
JavaScript shows alert "Item added to cart successfully!"
```

### 2. View Cart
```
User navigates to /cart
    ↓
Flask render_template("cart.html")
    ↓
cart.html loads in browser
    ↓
JavaScript onload: fetch('/api/cart')
    ↓
Flask get_cart():
    1. Query CartItem.filter_by(user_id=session['user_id'])
    2. For each CartItem:
       - Look up product in OFFER_PRODUCTS by product_id
       - Calculate total_price = product.price × quantity
       - Build response JSON
    3. Return {success, items, count, total_price}
    ↓
JavaScript receives JSON data
    ↓
JavaScript renders:
    - For each item: Create HTML with image, name, price, controls
    - Calculate and display: subtotal, shipping (£5.00), total
    - Update summary sidebar
```

### 3. Update Quantity
```
User clicks +/- button or changes input
    ↓
JavaScript captures new quantity value
    ↓
JavaScript sends PUT /api/cart/item/<item_id>
    ↓
Flask update_cart_item():
    1. Verify user owns this item
    2. Validate quantity >= 1
    3. CartItem.quantity = new_quantity
    4. db.session.commit()
    5. Return {success: True}
    ↓
JavaScript calls loadCart() to refresh display
    ↓
Fresh data fetched and UI updated
```

### 4. Remove Item
```
User clicks "Remove" button
    ↓
JavaScript shows confirm dialog
    ↓
User clicks OK
    ↓
JavaScript sends DELETE /api/cart/item/<item_id>
    ↓
Flask remove_from_cart():
    1. Verify user owns this item
    2. db.session.delete(CartItem)
    3. db.session.commit()
    4. Return {success: True}
    ↓
JavaScript calls loadCart() to refresh display
    ↓
Item removed from UI, totals recalculated
```

## Session Management

```
User Registers/Logs In
    ↓
Flask sets session['user_id'] = unique_user_id
    ↓
Session persists in browser (server-side)
    ↓
Every cart operation uses session['user_id'] to isolate data
    ↓
User logs out
    ↓
Flask session.clear()
    ↓
User loses access to their cart (redirected to login)
    ↓
If user logs back in with same account:
    ↓
Same session['user_id'] = same cart items restored
```

## Authentication & Authorization

```
All cart endpoints check:

1. if 'user_id' not in session:
   └─→ Return 401 Unauthorized
   
2. For DELETE/PUT:
   ├─→ Verify CartItem.user_id == session['user_id']
   └─→ Prevent users from modifying other users' carts

3. For GET /cart (page):
   ├─→ if not session.get('authenticated'):
   │   └─→ Redirect to login
   └─→ OK: Render cart.html
```

## Error Handling

```
Possible Errors & Responses:

Product not found (404):
  "error": "Product not found"

User not logged in (401):
  "error": "User not logged in"

Invalid quantity (400):
  "error": "Quantity must be at least 1"

Missing data (400):
  "error": "Product ID is required"

Database error (500):
  "error": "Error message"

All errors caught by try/except blocks
  ↓
Rollback database transaction on error
  ↓
Return JSON with error message
  ↓
JavaScript displays alert to user
```

## Frontend Components

### product_detail.html
- Add to Cart button (id="addToCartBtn")
- Event listener for click
- Validates login status
- Calls fetch() to POST /api/cart/add
- Shows success/error alert

### cart.html
- `loadCart()` - Fetches data from /api/cart
- `updateQuantity()` - Sends PUT request
- `removeFromCart()` - Sends DELETE request
- Dynamic HTML rendering from JSON response
- Order summary calculation
- Error handling and empty cart state

### Shared Features
- `escapeHtml()` - XSS protection
- Proper HTTP methods (GET, POST, PUT, DELETE)
- Content-Type: application/json
- Error messages and user feedback
- Loading indicators
- Responsive design

## Database Queries

```
SQLAlchemy ORM Queries:

# Create new item
new_item = CartItem(user_id=..., product_id=..., quantity=...)
db.session.add(new_item)
db.session.commit()

# Find existing item
item = CartItem.query.filter_by(
    user_id=session['user_id'],
    product_id=product_id
).first()

# Get all items for user
items = CartItem.query.filter_by(user_id=session['user_id']).all()

# Update quantity
item.quantity = new_quantity
db.session.commit()

# Delete item
db.session.delete(item)
db.session.commit()
```

## Security Measures

1. **Authentication**: All endpoints require session['user_id']
2. **Authorization**: Users can only access/modify their own items
3. **Input Validation**: Quantity >= 1, product exists
4. **XSS Protection**: escapeHtml() on all user data
5. **SQL Injection**: SQLAlchemy ORM prevents injection
6. **Database Transaction**: Rollback on error

## Performance Considerations

- **Indexed columns**: user_id, product_id (fast lookups)
- **AJAX loading**: Cart loads without page refresh
- **Client-side calculations**: Reduces server load for totals
- **Single database query**: Per operation (efficient)
- **Lazy loading**: Product details fetched only when needed

## Scalability Future Improvements

- Add caching for OFFER_PRODUCTS
- Implement pagination for large carts
- Add analytics/tracking for abandoned carts
- Implement cart persistence across sessions
- Add bulk operations (select multiple items)
