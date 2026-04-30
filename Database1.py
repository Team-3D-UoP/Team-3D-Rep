import sqlite3

# Connect to SQLite database (creates file if it doesn't exist)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# SQL script as a string
sql_script = """
DROP TABLE IF EXISTS EligibleParts;
DROP TABLE IF EXISTS UserResponses;
DROP TABLE IF EXISTS UserChats;
DROP TABLE IF EXISTS RegisteredParts;
DROP TABLE IF EXISTS Reviews;
DROP TABLE IF EXISTS CarOwners;
DROP TABLE IF EXISTS RegisteredCars;
DROP TABLE IF EXISTS Users;

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
UserID INT,
brand TEXT,
year TEXT,
part_name TEXT,
price REAL NOT NULL,
description TEXT,
image TEXT,
FOREIGN KEY (UserID) REFERENCES Users(UserID)
);


CREATE TABLE UserChats (
    ChatID INTEGER PRIMARY KEY,
    PartID INTEGER NOT NULL,
    UserID INTEGER NOT NULL,
    category TEXT,
    message TEXT NOT NULL,
    timestamp TEXT,
    FOREIGN KEY (PartID) REFERENCES RegisteredParts(PartID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE UserResponses (
    ResponseID INTEGER PRIMARY KEY,
    ChatID INTEGER NOT NULL,
    UserID INTEGER NOT NULL,
    response TEXT NOT NULL,
    FOREIGN KEY (ChatID) REFERENCES UserChats(ChatID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE EligibleParts (
    PartID INTEGER NOT NULL,
    CarID INTEGER NOT NULL,
    PRIMARY KEY (PartID, CarID),
    FOREIGN KEY (PartID) REFERENCES RegisteredParts(PartID),
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

 -- data for 5 Car Brands Toyota, Honda, BMW, Audi, Merceds.
INSERT INTO RegisteredParts (PartID, UserID, brand, year, part_name, price, description) VALUES

-- TOYOTA
(101,1,'Toyota',2026,'Oil Filter',27,'Toyota oil filter'),
(102,2,'Toyota',2024,'Headlight',92,'Toyota headlight'),
(103,2,'Toyota',2025,'Air Filter',32,'Toyota air filter'),
(104,2,'Toyota',2026,'Windshield Wiper',21,'Toyota wiper'),
(105,3,'Toyota',2024,'Exhaust',205,'Toyota exhaust'),
(106,3,'Toyota',2025,'Engine',1520,'Toyota engine'),
(107,3,'Toyota',2026,'Tyres',410,'Toyota tyres'),
(108,4,'Toyota',2024,'Battery',128,'Toyota battery'),
(109,4,'Toyota',2025,'Brake Pads',63,'Toyota brake pads'),
(110,4,'Toyota',2026,'Oil Filter',29,'Toyota oil filter'),
(111,5,'Toyota',2024,'Headlight',96,'Toyota headlight'),
(112,5,'Toyota',2025,'Air Filter',34,'Toyota air filter'),
(113,5,'Toyota',2026,'Windshield Wiper',23,'Toyota wiper'),
(114,6,'Toyota',2024,'Exhaust',215,'Toyota exhaust'),
(115,6,'Toyota',2025,'Engine',1580,'Toyota engine'),
(116,6,'Toyota',2026,'Tyres',430,'Toyota tyres'),
(117,7,'Toyota',2024,'Battery',126,'Toyota battery'),
(118,7,'Toyota',2025,'Brake Pads',64,'Toyota brake pads'),
(119,1,'Toyota',2026,'Oil Filter',30,'Toyota oil filter'),
(120,2,'Toyota',2024,'Headlight',98,'Toyota headlight'),

-- HONDA
(141,1,'Honda',2026,'Oil Filter',25,'Honda oil filter'),
(142,2,'Honda',2024,'Headlight',86,'Honda headlight'),
(143,2,'Honda',2025,'Air Filter',29,'Honda air filter'),
(144,2,'Honda',2026,'Windshield Wiper',19,'Honda wiper'),
(145,3,'Honda',2024,'Exhaust',192,'Honda exhaust'),
(146,3,'Honda',2025,'Engine',1420,'Honda engine'),
(147,3,'Honda',2026,'Tyres',385,'Honda tyres'),
(148,4,'Honda',2024,'Battery',119,'Honda battery'),
(149,4,'Honda',2025,'Brake Pads',61,'Honda brake pads'),
(150,4,'Honda',2026,'Oil Filter',27,'Honda oil filter'),
(151,5,'Honda',2024,'Headlight',89,'Honda headlight'),
(152,5,'Honda',2025,'Air Filter',31,'Honda air filter'),
(153,5,'Honda',2026,'Windshield Wiper',21,'Honda wiper'),
(154,6,'Honda',2024,'Exhaust',198,'Honda exhaust'),
(155,6,'Honda',2025,'Engine',1480,'Honda engine'),
(156,6,'Honda',2026,'Tyres',395,'Honda tyres'),
(157,7,'Honda',2024,'Battery',122,'Honda battery'),
(158,7,'Honda',2025,'Brake Pads',60,'Honda brake pads'),
(159,1,'Honda',2026,'Oil Filter',28,'Honda oil filter'),
(160,2,'Honda',2024,'Headlight',90,'Honda headlight'),

-- BMW
(181,1,'BMW',2026,'Oil Filter',37,'BMW oil filter'),
(182,2,'BMW',2024,'Headlight',122,'BMW headlight'),
(183,2,'BMW',2025,'Air Filter',41,'BMW air filter'),
(184,2,'BMW',2026,'Windshield Wiper',26,'BMW wiper'),
(185,3,'BMW',2024,'Exhaust',305,'BMW exhaust'),
(186,3,'BMW',2025,'Engine',2550,'BMW engine'),
(187,3,'BMW',2026,'Tyres',610,'BMW tyres'),
(188,4,'BMW',2024,'Battery',158,'BMW battery'),
(189,4,'BMW',2025,'Brake Pads',86,'BMW brake pads'),
(190,4,'BMW',2026,'Oil Filter',39,'BMW oil filter'),
(191,5,'BMW',2024,'Headlight',128,'BMW headlight'),
(192,5,'BMW',2025,'Air Filter',43,'BMW air filter'),
(193,5,'BMW',2026,'Windshield Wiper',28,'BMW wiper'),
(194,6,'BMW',2024,'Exhaust',315,'BMW exhaust'),
(195,6,'BMW',2025,'Engine',2650,'BMW engine'),
(196,6,'BMW',2026,'Tyres',630,'BMW tyres'),
(197,7,'BMW',2024,'Battery',154,'BMW battery'),
(198,7,'BMW',2025,'Brake Pads',83,'BMW brake pads'),
(199,1,'BMW',2026,'Oil Filter',40,'BMW oil filter'),
(200,2,'BMW',2024,'Headlight',130,'BMW headlight'),

-- AUDI
(221,1,'Audi',2026,'Oil Filter',35,'Audi oil filter'),
(222,2,'Audi',2024,'Headlight',117,'Audi headlight'),
(223,2,'Audi',2025,'Air Filter',39,'Audi air filter'),
(224,2,'Audi',2026,'Windshield Wiper',25,'Audi wiper'),
(225,3,'Audi',2024,'Exhaust',292,'Audi exhaust'),
(226,3,'Audi',2025,'Engine',2420,'Audi engine'),
(227,3,'Audi',2026,'Tyres',585,'Audi tyres'),
(228,4,'Audi',2024,'Battery',149,'Audi battery'),
(229,4,'Audi',2025,'Brake Pads',81,'Audi brake pads'),
(230,4,'Audi',2026,'Oil Filter',37,'Audi oil filter'),
(231,5,'Audi',2024,'Headlight',120,'Audi headlight'),
(232,5,'Audi',2025,'Air Filter',41,'Audi air filter'),
(233,5,'Audi',2026,'Windshield Wiper',27,'Audi wiper'),
(234,6,'Audi',2024,'Exhaust',297,'Audi exhaust'),
(235,6,'Audi',2025,'Engine',2470,'Audi engine'),
(236,6,'Audi',2026,'Tyres',605,'Audi tyres'),
(237,7,'Audi',2024,'Battery',151,'Audi battery'),
(238,7,'Audi',2025,'Brake Pads',80,'Audi brake pads'),
(239,1,'Audi',2026,'Oil Filter',38,'Audi oil filter'),
(240,2,'Audi',2024,'Headlight',122,'Audi headlight'),

-- MERCEDES
(261,1,'Mercedes',2026,'Oil Filter',42,'Mercedes oil filter'),
(262,2,'Mercedes',2024,'Headlight',132,'Mercedes headlight'),
(263,2,'Mercedes',2025,'Air Filter',46,'Mercedes air filter'),
(264,2,'Mercedes',2026,'Windshield Wiper',29,'Mercedes wiper'),
(265,3,'Mercedes',2024,'Exhaust',325,'Mercedes exhaust'),
(266,3,'Mercedes',2025,'Engine',2750,'Mercedes engine'),
(267,3,'Mercedes',2026,'Tyres',660,'Mercedes tyres'),
(268,4,'Mercedes',2024,'Battery',168,'Mercedes battery'),
(269,4,'Mercedes',2025,'Brake Pads',96,'Mercedes brake pads'),
(270,4,'Mercedes',2026,'Oil Filter',43,'Mercedes oil filter'),
(271,5,'Mercedes',2024,'Headlight',138,'Mercedes headlight'),
(272,5,'Mercedes',2025,'Air Filter',49,'Mercedes air filter'),
(273,5,'Mercedes',2026,'Windshield Wiper',31,'Mercedes wiper'),
(274,6,'Mercedes',2024,'Exhaust',335,'Mercedes exhaust'),
(275,6,'Mercedes',2025,'Engine',2850,'Mercedes engine'),
(276,6,'Mercedes',2026,'Tyres',680,'Mercedes tyres'),
(277,7,'Mercedes',2024,'Battery',164,'Mercedes battery'),
(278,7,'Mercedes',2025,'Brake Pads',94,'Mercedes brake pads'),
(279,1,'Mercedes',2026,'Oil Filter',44,'Mercedes oil filter'),
(280,2,'Mercedes',2024,'Headlight',140,'Mercedes headlight');



INSERT INTO UserChats (ChatID, PartID, UserID, category, message) VALUES        

-- BATTERY
(71, 1, 1, 'Battery', 'Is this battery new?'),
(72, 1, 2, 'Battery', 'Does it include warranty?'),
(73, 1, 3, 'Battery', 'Is it compatible with my car?'),
(74, 1, 4, 'Battery', 'Is installation included?'),

-- BRAKE PADS
(75, 2, 1, 'Brake Pads', 'Are these original?'),
(76, 2, 2, 'Brake Pads', 'Are they durable?'),
(77, 2, 3, 'Brake Pads', 'Do they fit most cars?'),
(78, 2, 4, 'Brake Pads', 'Are they suitable for daily use?'),

-- OIL FILTER
(79, 3, 1, 'Oil Filter', 'Is this compatible with my vehicle?'),
(80, 3, 2, 'Oil Filter', 'Is it genuine?'),
(81, 3, 3, 'Oil Filter', 'Is installation easy?'),

-- HEADLIGHT
(82, 4, 1, 'Headlight', 'Is this LED?'),
(83, 4, 2, 'Headlight', 'Does it come as a pair?'),
(84, 4, 3, 'Headlight', 'Is it waterproof?'),

-- AIR FILTER
(85, 5, 1, 'Air Filter', 'Is it washable?'),
(86, 5, 2, 'Air Filter', 'Is it reusable?'),
(87, 5, 3, 'Air Filter', 'Does it fit most vehicles?'),

-- WIPER
(88, 6, 1, 'Wiper', 'Is it suitable for all weather?'),
(89, 6, 2, 'Wiper', 'Does it fit all models?'),
(90, 6, 3, 'Wiper', 'Is it easy to install?'),

-- EXHAUST
(91, 7, 1, 'Exhaust', 'Is this original?'),
(92, 7, 2, 'Exhaust', 'Does it improve performance?'),
(93, 7, 3, 'Exhaust', 'Is installation included?'),

-- ENGINE
(94, 8, 1, 'Engine', 'Is this engine new?'),
(95, 8, 2, 'Engine', 'Does it come with warranty?'),
(96, 8, 3, 'Engine', 'Is it tested before sale?'),

-- TYRES
(97, 9, 1, 'Tyres', 'Are these tyres new?'),
(98, 9, 2, 'Tyres', 'Are they suitable for all seasons?'),
(99, 9, 3, 'Tyres', 'Do they come with warranty?'),
(100, 9, 4, 'Tyres', 'Are they fuel efficient?');

INSERT INTO UserResponses (ResponseID, ChatID, UserID, response) VALUES

-- YES RESPONSES
(61, 71, 2, 'Yes'),
(62, 72, 3, 'Yes, warranty included'),
(63, 75, 4, 'Yes'),
(64, 82, 5, 'Yes, LED'),
(65, 85, 6, 'Yes'),
(66, 94, 7, 'Yes'),
(67, 97, 2, 'Yes, brand new'),

-- NO RESPONSES
(68, 74, 3, 'No'),
(69, 77, 4, 'No, not for all cars'),
(70, 83, 5, 'No'),
(71, 89, 6, 'No, depends on model'),
(72, 93, 7, 'No, installation not included'),
(73, 98, 2, 'No, only for specific seasons'),

-- CUSTOMER SUPPORT RESPONSES
(75, 79, 4, 'For more information, please contact our sales team at sales@autopa
rtfinder.com'),
(76, 87, 5, 'For detailed enquiries, reach out to customer support at sales@auto
partfinder.com'),
(77, 92, 6, 'Please contact our support team at sales@autopartfinder.com for ass
istance'),
(78, 95, 7, 'For warranty details, email us at sales@autopartfinder.com'),      
(79, 100, 2, 'For further help, contact customer service at sales@autopartfinder
.com');


INSERT INTO EligibleParts (PartID, CarID) VALUES

-- Car 1
(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),

-- Car 2
(7,2),(8,2),(9,2),(10,2),(11,2),(12,2),

-- Car 3
(13,3),(14,3),(15,3),(16,3),(17,3),(18,3),

-- Car 4
(19,4),(20,4),(21,4),(22,4),(23,4),(24,4),

-- Car 5
(25,5),(26,5),(27,5),(28,5),(29,5),(30,5),

-- Car 6
(31,6),(32,6),(33,6),(34,6),(35,6),(36,6),

-- Car 7
(37,7),(38,7),(39,7),(40,7),(41,7),(42,7),

-- Car 8
(43,8),(44,8),(45,8),(46,8),(47,8),(48,8),

-- Car 9
(49,9),(50,9),(51,9),(52,9),(53,9),(54,9),

-- Car 10
(55,10),(56,10),(57,10),(58,10),(59,10),(60,10),

-- Car 11
(61,11),(62,11),(63,11),(64,11),(65,11),(66,11),

-- Car 12
(67,12),(68,12),(69,12),(70,12),(71,12),(72,12),

-- Car 13
(73,13),(74,13),(75,13),(76,13),(77,13),(78,13),

-- Car 14
(79,14),(80,14),(81,14),(82,14),(83,14),(84,14),

-- Car 15
(85,15),(86,15),(87,15),(88,15),(89,15),(90,15),

-- Car 16
(91,16),(92,16),(93,16),(94,16),(95,16),(96,16),

-- Car 17
(97,17),(98,17),(99,17),(100,17),(101,17),(102,17),

-- Car 18
(103,18),(104,18),(105,18),(106,18),(107,18),(108,18),

-- Car 19
(109,19),(110,19),(111,19),(112,19),(113,19),(114,19),

-- Car 20
(115,20),(116,20),(117,20),(118,20),(119,20),(120,20),

-- Car 21
(121,21),(122,21),(123,21),(124,21),(125,21),(126,21),

-- Car 22
(127,22),(128,22),(129,22),(130,22),(131,22),(132,22),

-- Car 23
(133,23),(134,23),(135,23),(136,23),(137,23),(138,23),

-- Car 24
(139,24),(140,24),(141,24),(142,24),(143,24),(144,24),

-- Car 25
(145,25),(146,25),(147,25),(148,25),(149,25),(150,25),

-- Car 26
(151,26),(152,26),(153,26),(154,26),(155,26),(156,26),

-- Car 27
(157,27),(158,27),(159,27),(160,27),(161,27),(162,27),

-- Car 28
(163,28),(164,28),(165,28),(166,28),(167,28),(168,28),

-- Car 29
(169,29),(170,29),(171,29),(172,29),(173,29),(174,29),

-- Car 30
(175,30),(176,30),(177,30),(178,30),(179,30),(180,30),

-- Car 31
(181,31),(182,31),(183,31),(184,31),(185,31),(186,31),

-- Car 32
(187,32),(188,32),(189,32),(190,32),(191,32),(192,32),

-- Car 33
(193,33),(194,33),(195,33),(196,33),(197,33),(198,33),

-- Car 34
(199,34),(200,34),(201,34),(202,34),(203,34),(204,34),

-- Car 35
(205,35),(206,35),(207,35),(208,35),(209,35),(210,35),

-- Car 36
(211,36),(212,36),(213,36),(214,36),(215,36),(216,36),

-- Car 37
(217,37),(218,37),(219,37),(220,37),(221,37),(222,37),

-- Car 38
(223,38),(224,38),(225,38),(226,38),(227,38),(228,38),

-- Car 39
(229,39),(230,39),(231,39),(232,39),(233,39),(234,39),

-- Car 40
(235,40),(236,40),(237,40),(238,40),(239,40),(240,40),

-- Car 41
(241,41),(242,41),(243,41),(244,41),(245,41),(246,41),

-- Car 42
(247,42),(248,42),(249,42),(250,42),(251,42),(252,42),

-- Car 43
(253,43),(254,43),(255,43),(256,43),(257,43),(258,43),

-- Car 44
(259,44),(260,44),(261,44),(262,44),(263,44),(264,44),

-- Car 45
(265,45),(266,45),(267,45),(268,45),(269,45),(270,45),

-- Car 46
(271,46),(272,46),(273,46),(274,46),(275,46),(276,46),

-- Car 47
(277,47),(278,47),(279,47),(280,47);
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
