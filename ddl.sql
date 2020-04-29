-- 1. Fields in a tuple related to dates and times should always have values.
-- 2. All fields in a tuple relating to details about a name (eg: Menu Item Name, First Name, etc) should always have a value.
-- 4. Customers must have a specified mobile number.

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
    isA VARCHAR(10) NOT NULL,
    CONSTRAINT CK_isA_MenuItem CHECK(isA IN ('Main', 'Side', 'Dessert'))
);
CREATE TABLE Customer(
    customerId INTEGER PRIMARY KEY,
    firstName VARCHAR(30) NOT NULL,
    lastName VARCHAR(30) NOT NULL,
    address VARCHAR(100),
    mobileNo CHAR(10) NOT NULL
);
CREATE TABLE Courier(
    courierId INTEGER PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    address VARCHAR(100),
    mobile CHAR(10)
);
CREATE TABLE Delivery(
    deliveryId INTEGER PRIMARY KEY,
    courierId INTEGER NOT NULL,
    timeReady TIMESTAMP NOT NULL,
    timeDelivered TIMESTAMP NOT NULL,
    CONSTRAINT FK_courierId_Delivery FOREIGN KEY (courierId) REFERENCES Courier,
    CONSTRAINT CK_timeConflict_Delivery CHECK(timeReady < timeDelivered)
);
CREATE TABLE Contains(
    menuId INTEGER,
    menuItemId INTEGER,
    PRIMARY KEY (menuId, menuItemId),
    CONSTRAINT FK_menuId_MenuContains FOREIGN KEY (menuId) REFERENCES Menu ON DELETE CASCADE,
    CONSTRAINT FK_menuItemId_MenuContains FOREIGN KEY (menuItemId) REFERENCES MenuItem ON DELETE CASCADE
);
CREATE TABLE "Order"(
    orderId INTEGER PRIMARY KEY,
    customerId INTEGER NOT NULL,
    staffId INTEGER NOT NULL,
    deliveryId INTEGER NOT NULL,
    -- using reserved words like DATETIME to name columns is bad practice
    datetime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    totalCharge FLOAT NOT NULL,
    CONSTRAINT FK_customerId_Order FOREIGN KEY (customerId) REFERENCES Customer ON DELETE CASCADE,
    CONSTRAINT FK_staffId_Order FOREIGN KEY (staffId) REFERENCES Staff, -- ON DELETE CASCADE?
    CONSTRAINT FK_deliveryId_Order FOREIGN KEY (deliveryId) REFERENCES Delivery ON DELETE CASCADE, -- necessary?
    CONSTRAINT CK_totalCharge_Order CHECK(totalCharge > 0)
);
CREATE TABLE OrderItem(
    orderItemId INTEGER PRIMARY KEY,
    orderId INTEGER NOT NULL,
    customerId INTEGER NOT NULL,
    menuItemId INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    charge FLOAT NOT NULL,
    CONSTRAINT FK_orderId_OrderItem FOREIGN KEY (orderId) REFERENCES "Order" ON DELETE CASCADE,
    CONSTRAINT FK_customerId_OrderItem FOREIGN KEY (customerId) REFERENCES Customer, -- ON DELETE CASCADE?
    CONSTRAINT FK_menuItemId_OrderItem FOREIGN KEY (menuItemId) REFERENCES MenuItem, -- ON DELETE CASCADE?
    CONSTRAINT CK_quantity_OrderItem CHECK(quantity > 0)
    -- add check - ensure order and order item matches
    -- what about item price and order match? check that too?
);
