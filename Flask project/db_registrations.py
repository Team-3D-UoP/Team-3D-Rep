import sqlite3
import os
from pathlib import Path
from flask import session
from datetime import datetime

db_path = db_path = os.path.join(os.path.dirname(__file__), '../database.db')

def insert_registered_part(brand, year, part_name, price, description, image=None, user_id=None):
    # Get the currently logged-in user ID from session if not provided
    user_id = 1
    
    if not user_id:
        return {
            'success': False,
            'message': 'User not logged in',
            'part_id': None
        }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Insert the part into RegisteredParts table
        cursor.execute('''
            INSERT INTO RegisteredParts 
            (UserID, brand, year, part_name, price, description, image)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, brand, year, part_name, price, description, image))
        
        # Get the auto-incremented PartID
        part_id = cursor.lastrowid
        
        conn.commit()

        cursor.execute(
            'SELECT * FROM RegisteredParts WHERE UserID = ? AND brand = ? AND part_name = ?',
            (user_id, brand, part_name)
        )
        print(cursor.fetchall())

        conn.close()
        
        return {
            'success': True,
            'message': f'Part registered successfully with ID {part_id}',
            'part_id': part_id
        }
    
    except sqlite3.IntegrityError as e:
        return {
            'success': False,
            'message': f'Database integrity error: {str(e)}',
            'part_id': None
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': f'Error inserting part: {str(e)}',
            'part_id': None
        }