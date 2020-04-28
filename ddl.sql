-- example
CREATE TABLE Example(
    staffid INTEGER PRIMARY KEY,
    position VARCHAR(20) NOT NULL,
    name INTEGER DEFAULT 1,
    birthday DATE NULL,
    age INTEGER CHECK( age >= 0 AND age < 150),
    country VARCHAR(20),
    -- if composite PK
    PRIMARY KEY (sid,uos),
    FOREIGN KEY (sid) REFERENCES Student,

    -- the on delete cascade conveys
    -- that an enrolled row should be
    -- deleted when the student with sid
    -- that it refers to is deleted
    ON DELETE CASCADE

    -- the on update set default
    -- will attempt to update the
    -- value of sid to a default value
    -- that is specified as the default
    -- in this Enrolled schema definition
    ON UPDATE SET DEFAULT

    REFERENCES Student ON DELETE CASCADE,
    REFERENCES UnitOfStudy ON DELETE CASCADE,

    CONSTRAINT PK_enrolled PRIMARY KEY (sid,uos)
    CONSTRAINT FK_sid_enrolled FOREIGN KEY (sid)
    CONSTRAINT CK_grade_enrolled CHECK(grade IN ('F', 'A')),
);
-- constraints: UNIQUE, NOT NULL, UNIQUE, DEFAULT, CHECK,

CREATE TABLE Staff(
    staffid INTEGER PRIMARY KEY,
    position VARCHAR(20),
    name VARCHAR(20) NOT NULL
);
CREATE TABLE Menu(
    menuId INTEGER PRIMARY KEY,
    description VARCHAR(100)
);
CREATE TABLE MenuItem(
    menuItemId INTEGER PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    price FLOAT NOT NULL,
    description VARCHAR(100),
    itemType VARCHAR(10) NOT NULL,
    CONSTRAINT CK_itemType_MenuItem CHECK(itemType IN ('Main', 'Side', 'Dessert'))
);
CREATE TABLE MenuContains(
    menuId INTEGER,
    menuItemId INTEGER,
    PRIMARY KEY (menuId, menuItemId),
    CONSTRAINT FK_menuId_MenuContains FOREIGN KEY (menuId) REFERENCES Menu,
    CONSTRAINT FK_menuItemId_MenuContains FOREIGN KEY (menuItemId) REFERENCES MenuItem
);
CREATE TABLE OrderItem(
    orderItemId INTEGER PRIMARY KEY,
    orderId INTEGER NOT NULL,
    customerId INTEGER NOT NULL,
    menuItemId INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    charge FLOAT NOT NULL,
    CONSTRAINT FK_orderId_OrderItem FOREIGN KEY (orderId) REFERENCES Order,
    CONSTRAINT FK_customerId_OrderItem FOREIGN KEY (customerId) REFERENCES Customer,
    CONSTRAINT FK_menuItemId_OrderItem FOREIGN KEY (menuItemId) REFERENCES MenuItem,
    CONSTRAINT CK_quantity_OrderItem CHECK(quantity > 0)
);
CREATE TABLE Order(
    orderId INTEGER PRIMARY KEY,
    customerId INTEGER NOT NULL,
    staffId INTEGER NOT NULL,
    deliveryId INTEGER NOT NULL,
    -- using reserved words like DATETIME to name columns is bad practice
    dt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    totalCharge FLOAT NOT NULL,
    CONSTRAINT FK_customerId_Order FOREIGN KEY (customerId) REFERENCES Customer,
    CONSTRAINT FK_staffId_Order FOREIGN KEY (staffId) REFERENCES Staff,
    CONSTRAINT FK_deliveryId_Order FOREIGN KEY (deliveryId) REFERENCES Delivery,
    CONSTRAINT CK_totalCharge_Order CHECK(totalCharge > 0)
);
CREATE TABLE Customer(
    customerId INTEGER PRIMARY KEY,
    firstName VARCHAR(30) NOT NULL,
    lastName VARCHAR(30) NOT NULL,
    address VARCHAR(100) NOT NULL,
    mobileNumber INTEGER NOT NULL
);
CREATE TABLE Delivery(
    deliveryId INTEGER PRIMARY KEY,
    courierId INTEGER NOT NULL,
    timeReady TIMESTAMP NOT NULL,
    timeDelivered TIMESTAMP NOT NULL, -- Not null? where will data be before delivery is complete?
    CONSTRAINT FK_courierId_Delivery FOREIGN KEY (courierId) REFERENCES Courier,
    CONSTRAINT CK_timeConflict_Delivery CHECK(timeReady < timeDelivered)
);
CREATE TABLE Courier(
    courierId INTEGER PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    address VARCHAR(100), -- NOT NULL?
    mobileNumber INTEGER -- NOT NULL?
);
