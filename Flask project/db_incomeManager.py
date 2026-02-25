import sqlite3

def addIncomes(user, empl, savings):
    connection = sqlite3.connect("taxcalculator.db")
    cursor = connection.cursor()
    query = "INSERT INTO Incomes (empl, savings) VALUES (?, ?)"
    cursor.execute(query, (empl, savings))
    connection.commit()
    print("Saved")

def retrieveIncomes():
    connection = sqlite3.connect("taxcalculator.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Incomes")    
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    return rows

def deleteIncomes():
    connection = sqlite3.connect("taxcalculator.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Incomes")    
    connection.commit()

if __name__ == "__main__":
    retrieveIncomes()