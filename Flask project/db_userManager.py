import sqlite3

def createTableUser():
    connection = sqlite3.connect("taxcalculator.db")
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Users (id INTEGER PRIMARY KEY, name text NOT NULL);")    
    connection.commit()


def addUser(id, name):
    connection = sqlite3.connect("taxcalculator.db")
    cursor = connection.cursor()
    query = "INSERT INTO Users (id, name) VALUES (?, ?)"
    cursor.execute(query, (id, name))
    connection.commit()
    print("Saved")

def retrieveUsers():
    connection = sqlite3.connect("taxcalculator.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Users")    
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    return rows

if __name__ == "__main__":
    createTableUser()
    addUser(2, "Jane")
    retrieveUsers()