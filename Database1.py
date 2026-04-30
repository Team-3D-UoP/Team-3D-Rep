import sqlite3

# Connect to SQLite database (creates file if it doesn't exist)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# SQL script as a string
sql_script = """
CREATE TABLE IF NOT EXISTS Users (
    UserID INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE
    );

CREATE TABLE IF NOT EXISTS CarOwners (
    UserID INT NOT NULL,
    CarID INT NOT NULL,
    PRIMARY KEY (UserID, CarID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (CarID) REFERENCES RegisteredCars(CarID)
    );

CREATE TABLE IF NOT EXISTS RegisteredCars (
    CarID INTEGER PRIMARY KEY AUTOINCREMENT,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    year TEXT NOT NULL,
    license TEXT NOT NULL UNIQUE,
    engine TEXT,
    wheels TEXT DEFAULT NULL
    );

CREATE TABLE IF NOT EXISTS Reviews (
ReviewID INTEGER PRIMARY KEY AUTOINCREMENT,
UserID INT,
rating INT DEFAULT NULL,
details TEXT,
FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE IF NOT EXISTS RegisteredParts (
PartID INTEGER PRIMARY KEY AUTOINCREMENT,
CarID INT,
name TEXT NOT NULL,
price REAL NOT NULL,
description TEXT,
image TEXT,
FOREIGN KEY (CarID) REFERENCES RegisteredCars(CarID)
);


-- Users
INSERT INTO Users (email, username) VALUES
('olivergrant@gmail.com','olivergrant'),
('ameliawright@gmail.com','ameliawright'),
('jackturner@gmail.com','jackturner'),
('islafoster@gmail.com','islafoster'),
('harrycoleman@gmail.com','harrycoleman'),
('emilyharrison@gmail.com','emilyharrison'),
('georgemason@gmail.com','georgemason'),
('avachapman@gmail.com','avachapman'),
('noahellis@gmail.com','noahellis'),
('mialawson@gmail.com','mialawson'),
('leowebster@gmail.com','leowebster'),
('gracemitchell@gmail.com','gracemitchell'),
('oscarhughes@gmail.com','oscarhughes'),
('lilywatson@gmail.com','lilywatson'),
('archieward@gmail.com','archieward'),
('evagibson@gmail.com','evagibson'),
('theojenkins@gmail.com','theojenkins'),
('sophialloyd@gmail.com','sophialloyd'),
('freddiehunt@gmail.com','freddiehunt'),
('isabellexford@gmail.com','isabellexford'),
('alfiehamilton@gmail.com','alfiehamilton'),
('charlotterussell@gmail.com','charlotterussell'),
('ethanmatthews@gmail.com','ethanmatthews'),
('harpergriffin@gmail.com','harpergriffin'),
('jacobfisher@gmail.com','jacobfisher'),
('ellawarren@gmail.com','ellawarren'),
('thomasdixon@gmail.com','thomasdixon'),
('lucycrawford@gmail.com','lucycrawford'),
('jamesporter@gmail.com','jamesporter'),
('chloyelliott@gmail.com','chloyelliott'),
('lukesimpson@gmail.com','lukesimpson'),
('rubymcdonald@gmail.com','rubymcdonald'),
('benjaminstevens@gmail.com','benjaminstevens'),
('rosiepayne@gmail.com','rosiepayne'),
('samuelpearson@gmail.com','samuelpearson'),
('hollybennett@gmail.com','hollybennett'),
('danielwood@gmail.com','danielwood');

-- CarOwners, linking Users to RegisteredCars
INSERT INTO CarOwners (UserID, CarID) VALUES
-- Users with 2 cars (1–13)
(1,1),(1,2),
(2,3),(2,4),
(3,5),(3,6),
(4,7),(4,8),
(5,9),(5,10),
(6,11),(6,12),
(7,13),(7,37),
(8,15),(8,16),
(9,17),(9,18),
(10,24),(10,28),
(11,21),(11,22),
(12,23),(12,19),
(13,25),(13,26),

-- Users with 1 car (14–37)
(14,27),
(15,20),
(16,29),
(17,30),
(18,31),
(19,32),
(20,33),
(21,34),
(22,35),
(23,36),
(24,14),
(25,38),
(26,39),
(27,40),
(28,41),
(29,42),
(30,43),
(31,44),
(32,45),
(33,46),
(34,47),
(35,48),
(36,49),
(37,50);


-- RegisteredCars
INSERT INTO RegisteredCars (make, model, year, license, engine, wheels) VALUES
-- Toyota (Corolla, RAV4)
('Toyota','Corolla','2024','TOY001','1.8L Hybrid','Alloy'),
('Toyota','Corolla','2024','TOY007','1.8L Hybrid','Steel'),
('Toyota','Corolla','2025','TOY002','1.8L Hybrid','Steel'),
('Toyota','Corolla','2025','TOY005','2.0L Petrol','Steel'),
('Toyota','Corolla','2026','TOY009','2.0L Petrol','Alloy'),

('Toyota','RAV4','2024','TOY019','2.5L Hybrid AWD','Steel'),
('Toyota','RAV4','2025','TOY011','2.5L Hybrid','Alloy'),
('Toyota','RAV4','2026','TOY012','2.5L Hybrid','All-Terrain'),
('Toyota','RAV4','2025','TOY014','2.5L Hybrid AWD','Alloy'),
('Toyota','RAV4','2026','TOY015','2.5L Hybrid AWD','All-Terrain'),

-- Honda (Civic, CR-V)
('Honda','Civic','2024','HON001','2.0L Petrol','Alloy'),
('Honda','Civic','2025','HON002','2.0L Petrol','Steel'),
('Honda','Civic','2026','HON003','2.0L Petrol','Alloy'),
('Honda','Civic','2024','HON004','1.5L Turbo','Sport'),
('Honda','Civic','2025','HON005','1.5L Turbo','Alloy'),

('Honda','CR-V','2025','HON011','2.0L Hybrid','Alloy'),
('Honda','CR-V','2026','HON012','2.0L Hybrid AWD','All-Terrain'),
('Honda','CR-V','2024','HON013','2.0L Hybrid','Steel'),
('Honda','CR-V','2025','HON014','2.0L Hybrid AWD','Alloy'),
('Honda','CR-V','2026','HON015','2.0L Hybrid AWD','All-Terrain'),

-- BMW (3 Series, X5)
('BMW','3 Series','2024','BMW001','2.0L Turbo','Alloy'),
('BMW','3 Series','2025','BMW002','2.0L Turbo','Sport'),
('BMW','3 Series','2026','BMW003','2.0L Turbo','Alloy'),
('BMW','3 Series','2024','BMW004','3.0L Turbo','Sport'),
('BMW','3 Series','2025','BMW005','3.0L Turbo','Alloy'),

('BMW','X5','2026','BMW012','3.0L Hybrid','All-Terrain'),
('BMW','X5','2024','BMW013','3.0L Diesel','Alloy'),
('BMW','X5','2025','BMW014','3.0L Hybrid','All-Terrain'),
('BMW','X5','2026','BMW015','3.0L Hybrid','Alloy'),
('BMW','X5','2024','BMW016','3.0L Diesel','Steel'),

-- Audi (A4, Q5)
('Audi','A4','2024','AUD001','2.0L Petrol','Alloy'),
('Audi','A4','2025','AUD002','2.0L Diesel','Alloy'),
('Audi','A4','2026','AUD003','2.0L Hybrid','Sport'),
('Audi','A4','2024','AUD004','2.0L Petrol','Alloy'),
('Audi','A4','2025','AUD005','2.0L Diesel','Sport'),

('Audi','Q5','2025','AUD011','2.0L Hybrid','Alloy'),
('Audi','Q5','2026','AUD012','2.0L Hybrid AWD','All-Terrain'),
('Audi','Q5','2024','AUD013','2.0L Diesel','Steel'),
('Audi','Q5','2025','AUD014','2.0L Hybrid AWD','Alloy'),
('Audi','Q5','2026','AUD015','2.0L Hybrid AWD','All-Terrain'),

-- Mercedes (C-Class, GLC)
('Mercedes','C-Class','2024','MER001','2.0L Hybrid','Alloy'),
('Mercedes','C-Class','2025','MER002','2.0L Hybrid','Sport'),
('Mercedes','C-Class','2026','MER003','2.0L Hybrid','Alloy'),
('Mercedes','C-Class','2024','MER004','2.0L Petrol','Sport'),
('Mercedes','C-Class','2025','MER005','2.0L Petrol','Alloy'),

('Mercedes','GLC','2025','MER011','2.0L Diesel','All-Terrain'),
('Mercedes','GLC','2026','MER012','2.0L Hybrid','All-Terrain'),
('Mercedes','GLC','2024','MER013','2.0L Diesel','Alloy'),
('Mercedes','GLC','2025','MER014','2.0L Hybrid','All-Terrain'),
('Mercedes','GLC','2026','MER015','2.0L Hybrid','Alloy');


INSERT INTO Reviews (UserID, rating, details) VALUES
(1, 5, 'Excellent car, very reliable and fuel-efficient.'),
(2, 4, 'Great performance but a bit pricey.'),
(3, 3, 'Decent car but had some minor issues.'),
(4, 5, 'Love this car! Smooth ride and stylish design.'),
(5, 4, 'Good value for the money.'),
(6, 2, 'Not satisfied with the engine performance.'),
(7, 5, 'Best car I have ever owned! Highly recommend it.'),
(8, 3, 'Average car with no standout features.'),
(9, 4, 'Comfortable and spacious interior.'),
(10, 5, 'Fantastic car with great handling and features.');
"""

# Split the script into individual statements
statements = sql_script.split(';')

# Execute each statement
for statement in statements:
    statement = statement.strip()
    if statement:
        cursor.execute(statement)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database created successfully.")
