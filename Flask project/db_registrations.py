import sqlite3
import os
from pathlib import Path
from flask import session
from datetime import datetime

db_reg_path = os.path.join(os.path.dirname(__file__), 'database.db')

def select_user_id(email, username):
    conn = sqlite3.connect(db_reg_path)
    cursor = conn.cursor()

    cursor.execute(
        'SELECT UserID FROM Users WHERE email = ? AND username = ?',
        (email, username)
    )
    output = cursor.fetchall()
    print(output)
    conn.close()
    
    return output

def insert_new_user(email, username):
    try:
        conn = sqlite3.connect(db_reg_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO Users (email, username)
            VALUES (?, ?)
        ''', (email, username))
        
        conn.commit()

        cursor.execute(
            'SELECT * FROM Users WHERE email = ? AND username = ?',
            (email, username)
        )
        print(cursor.fetchall())

        conn.close()
    
    except sqlite3.IntegrityError as e:
        print(f"Database integrity error: {str(e)}")
    
    except Exception as e:
        print(f"Error inserting user: {str(e)}")

def insert_registered_part(user_id, brand, year, part_name, price, description, image):
    try:
        conn = sqlite3.connect(db_reg_path)
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

def insert_registered_car(make, model, year, license, engine, wheels, user_id):    
    try:
        conn = sqlite3.connect(db_reg_path)
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