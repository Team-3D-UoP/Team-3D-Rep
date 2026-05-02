"""
Script to import car parts from database.db RegisteredParts table
and create them as products in the Flask app
"""

import sqlite3
import sys
from datetime import datetime

# Database paths
SOURCE_DB = 'database.db'
TARGET_DB = 'Flask project/instance/team3d.db'

def get_parts_from_database():
    """Query all RegisteredParts from the source database"""
    try:
        conn = sqlite3.connect(SOURCE_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
        SELECT
            PartID,
            brand,
            year,
            part_name,
            price,
            description,
            image
        FROM RegisteredParts
        ORDER BY brand, part_name
        """

        cursor.execute(query)
        parts = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return parts
    except Exception as e:
        print(f"Error reading from database: {e}")
        return []

def create_product_from_part(part):
    """Convert a RegisteredPart to a product dict"""

    # Create seller ID based on brand
    seller_map = {
        'Toyota': 1,
        'Honda': 2,
        'BMW': 3,
        'Audi': 4,
        'Mercedes': 5
    }

    seller_id = seller_map.get(part['brand'], 1)

    # Calculate discount (10-20% depending on part type)
    base_price = float(part['price'])
    discount_percent = 15  # Default 15% discount

    if part['part_name'] in ['Engine', 'Tyres']:
        discount_percent = 10  # Less discount for expensive parts
    elif part['part_name'] in ['Oil Filter', 'Air Filter', 'Windshield Wiper']:
        discount_percent = 20  # More discount for cheap parts

    old_price = base_price / (1 - discount_percent / 100)
    current_price = base_price

    product = {
        'name': f"{part['brand']} {part['part_name']} ({part['year']})",
        'description': part['description'] or f"{part['brand']} {part['part_name']} for {part['year']} models",
        'old_price': round(old_price, 2),
        'current_price': round(current_price, 2),
        'discount_percent': discount_percent,
        'seller_id': seller_id,
        'brand': part['brand'],
        'part_type': part['part_name'],
        'year': part['year'],
        'image': part['image'] or f"part_{part['PartID']}.jpg"
    }

    return product

def insert_products_to_flask_db(products):
    """Insert all products into Flask SQLite database"""
    try:
        conn = sqlite3.connect(TARGET_DB)
        cursor = conn.cursor()

        # Check if products table exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            old_price REAL,
            current_price REAL,
            discount_percent INTEGER,
            seller_id INTEGER,
            image TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (seller_id) REFERENCES sellers(id)
        )
        """)

        # Insert products
        insert_count = 0
        for product in products:
            try:
                cursor.execute("""
                INSERT INTO products
                (name, description, old_price, current_price, discount_percent, seller_id, image)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    product['name'],
                    product['description'],
                    product['old_price'],
                    product['current_price'],
                    product['discount_percent'],
                    product['seller_id'],
                    product['image']
                ))
                insert_count += 1
            except Exception as e:
                print(f"Error inserting product {product['name']}: {e}")

        conn.commit()
        conn.close()

        return insert_count

    except Exception as e:
        print(f"Error connecting to Flask database: {e}")
        return 0

def main():
    """Main import function"""
    print("=" * 60)
    print("Car Parts to Products Importer")
    print("=" * 60)

    # Step 1: Get parts from source database
    print("\n[1/3] Reading car parts from database.db...")
    parts = get_parts_from_database()

    if not parts:
        print("❌ No parts found in database!")
        return False

    print(f"✓ Found {len(parts)} car parts")

    # Step 2: Convert parts to products
    print("\n[2/3] Converting parts to products...")
    products = [create_product_from_part(part) for part in parts]
    print(f"✓ Converted {len(products)} parts to products")

    # Display sample products
    print("\n📦 Sample Products:")
    for product in products[:5]:
        print(f"  - {product['name']}")
        print(f"    Price: £{product['current_price']} (was £{product['old_price']})")
        print(f"    Discount: {product['discount_percent']}%")
        print()

    # Step 3: Insert into Flask database
    print("[3/3] Inserting products into Flask database...")
    inserted = insert_products_to_flask_db(products)

    if inserted > 0:
        print(f"\n✅ Successfully imported {inserted} products!")
        print(f"   Total car parts imported: {inserted}/280")
        return True
    else:
        print("\n❌ Failed to insert products into Flask database")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
