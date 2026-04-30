CREATE TABLE RegisteredParts (
    PartID INTEGER PRIMARY KEY,
    UserID INTEGER NOT NULL,
    price REAL NOT NULL,
    description TEXT NOT NULL,
    image TEXT,
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE UserChats (
    ChatID INTEGER PRIMARY KEY,
    PartID INTEGER NOT NULL,
    UserID INTEGER NOT NULL,
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