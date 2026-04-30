import sqlite3
import os
from pathlib import Path
from flask import session
from datetime import datetime

db_path = os.path.join(os.path.dirname(__file__), '../database.db')

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
            'SELECT * FROM RegisteredParts WHERE PartID = ?',
            (part_id,)
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

def insert_registered_car(make, model, year, license, engine=None, wheels=None, user_id=None):
    # Get the currently logged-in user ID from session if not provided
    user_id = 1
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Insert the car into RegisteredCars table
        cursor.execute('''
            INSERT INTO RegisteredCars 
            (make, model, year, license, engine, wheels)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (make, model, year, license, engine, wheels))
        
        # Get the auto-incremented CarID
        car_id = cursor.lastrowid
        
        conn.commit()

        # Link the car to the user in CarOwners table
        cursor.execute('''
            INSERT INTO CarOwners 
            (CarID, UserID)
            VALUES (?, ?)
        ''', (car_id, user_id))
        
        conn.commit()

        cursor.execute(
            'SELECT * FROM RegisteredCars WHERE CarID = ?',
            (car_id,)
        )
        print(cursor.fetchall())

        cursor.execute(
            'SELECT * FROM CarOwners WHERE CarID = ? AND UserID = ?',
            (car_id, user_id)
        )
        print(cursor.fetchall())

        conn.close()
        
        return {
            'success': True,
            'message': f'Car registered successfully with ID {car_id}',
            'car_id': car_id
        }
    
    except sqlite3.IntegrityError as e:
        return {
            'success': False,
            'message': f'Database integrity error: {str(e)}',
            'car_id': None
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': f'Error inserting car: {str(e)}',
            'car_id': None
        }