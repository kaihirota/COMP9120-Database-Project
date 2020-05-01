-- we did not include ON DELETE CACADE to some tables that had foreign keys,
-- because we thought it would put the data at risk of being deleted unintentionally.
DROP TABLE IF EXISTS Staff CASCADE;
DROP TABLE IF EXISTS Menu CASCADE;
DROP TABLE IF EXISTS MenuItem CASCADE;
DROP TABLE IF EXISTS Main CASCADE;
DROP TABLE IF EXISTS Side CASCADE;
DROP TABLE IF EXISTS Dessert CASCADE;
DROP TABLE IF EXISTS Customer CASCADE;
DROP TABLE IF EXISTS Courier CASCADE;
DROP TABLE IF EXISTS Delivery CASCADE;
DROP TABLE IF EXISTS Contains CASCADE;
DROP TABLE IF EXISTS "Order" CASCADE;
DROP TABLE IF EXISTS OrderItem CASCADE;

CREATE TABLE Staff(
    staffId INTEGER PRIMARY KEY,
    position VARCHAR(20),
    name VARCHAR(30) NOT NULL
);
CREATE TABLE Menu(
    menuId INTEGER PRIMARY KEY,
    description VARCHAR(100)
);
CREATE TABLE MenuItem(
    menuItemId INTEGER PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    description VARCHAR(100)
);
CREATE TABLE Main(
    menuItemId INTEGER PRIMARY KEY,
    CONSTRAINT FK_menuItemId_Main FOREIGN KEY (menuItemId)
    REFERENCES MenuItem
    ON UPDATE CASCADE
    ON DELETE CASCADE
    DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE Side(
    menuItemId INTEGER PRIMARY KEY,
    CONSTRAINT FK_menuItemId_Side FOREIGN KEY (menuItemId)
    REFERENCES MenuItem
    ON UPDATE CASCADE
    ON DELETE CASCADE
    DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE Dessert(
    menuItemId INTEGER PRIMARY KEY,
    CONSTRAINT FK_menuItemId_Dessert FOREIGN KEY (menuItemId)
    REFERENCES MenuItem
    ON UPDATE CASCADE
    ON DELETE CASCADE
    DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE Customer(
    customerId INTEGER PRIMARY KEY,
    firstName VARCHAR(30) NOT NULL,
    lastName VARCHAR(30) NOT NULL,
    address VARCHAR(100) NOT NULL,
    mobileNo CHAR(10) NOT NULL
);
CREATE TABLE Courier(
    courierId INTEGER PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    address VARCHAR(100),
    mobile CHAR(10) NOT NULL
);
CREATE TABLE Delivery(
    deliveryId INTEGER PRIMARY KEY,
    courierId INTEGER NOT NULL,
    timeReady TIMESTAMP NOT NULL,
    timeDelivered TIMESTAMP NOT NULL,
    CONSTRAINT FK_courierId_Delivery FOREIGN KEY (courierId)
    REFERENCES Courier ON UPDATE CASCADE,
    CONSTRAINT CK_timeConflict_Delivery CHECK(timeReady < timeDelivered)
);
CREATE TABLE Contains(
    menuId INTEGER,
    menuItemId INTEGER,
    PRIMARY KEY (menuId, menuItemId),
    CONSTRAINT FK_menuId_Contains FOREIGN KEY (menuId)
    REFERENCES Menu (menuId)
    ON UPDATE CASCADE
    ON DELETE CASCADE
    DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT FK_menuItemId_Contains FOREIGN KEY (menuItemId)
    REFERENCES MenuItem (menuItemId)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);
CREATE TABLE "Order"(
    orderId INTEGER,
    customerId INTEGER,
    staffId INTEGER NOT NULL,
    deliveryId INTEGER NOT NULL,
    -- using reserved words like DATETIME to name columns is bad practice
    datetime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    totalCharge FLOAT NOT NULL,
    PRIMARY KEY (orderId, customerId),
    CONSTRAINT FK_customerId_Order FOREIGN KEY (customerId)
    REFERENCES Customer ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT FK_staffId_Order FOREIGN KEY (staffId)
    REFERENCES Staff ON UPDATE CASCADE,
    CONSTRAINT FK_deliveryId_Order FOREIGN KEY (deliveryId)
    REFERENCES Delivery ON UPDATE CASCADE,
    CONSTRAINT CK_totalCharge_Order CHECK(totalCharge > 0)
);
CREATE TABLE OrderItem(
    orderItemId INTEGER,
    orderId INTEGER,
    customerId INTEGER,
    menuItemId INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    charge NUMERIC(10, 2) NOT NULL,
    PRIMARY KEY (orderItemId, orderId, customerId),
    CONSTRAINT FK_orderId_OrderItem FOREIGN KEY (orderId, customerId)
    REFERENCES "Order" ON UPDATE CASCADE ON DELETE CASCADE,

    -- Doesn't delete on cascade because even if menuitems get deleted, it
    -- wouldn't be ideal to lose past transactions
    CONSTRAINT FK_menuItemId_OrderItem FOREIGN KEY (menuItemId)
    REFERENCES MenuItem ON UPDATE CASCADE,
    -- we didn't add constraint (trigger) to check if the total fee matches the
    -- individual items because we may have to account for overhead cost such as
    -- delivery fee and tax
    CONSTRAINT CK_quantity_OrderItem CHECK(quantity > 0)
);


-- menu must have at least 1 item
CREATE OR REPLACE FUNCTION menuMinimum1() RETURNS TRIGGER AS $menuMinimum1$
BEGIN
    IF new.menuId NOT IN (
        SELECT menuId FROM Contains
    )
    THEN RAISE EXCEPTION 'Menu must contain at least 1 item prior to insertion';
    END IF;
    RETURN NULL;
END;
$menuMinimum1$ LANGUAGE plpgsql;

-- add the trigger as a constraint on menu
CREATE CONSTRAINT TRIGGER Trigger_MenuContains
AFTER INSERT OR UPDATE OR DELETE ON Menu
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE PROCEDURE menuMinimum1();


-- menuitem can only be one of Main, Side, Dessert
CREATE OR REPLACE FUNCTION menuTotalParticipation()
  RETURNS TRIGGER AS $menuTotalParticipation$
BEGIN
    IF new.menuItemId IN (
        SELECT mi.menuItemId
        FROM MenuItem AS mi
        LEFT JOIN (
            SELECT menuItemId FROM Main
            UNION ALL
            SELECT menuItemId FROM Side
            UNION ALL
            SELECT menuItemId FROM Dessert
        ) AS items ON items.menuItemId = mi.menuItemId
        GROUP BY mi.menuItemId
        HAVING COUNT(mi.menuItemId) != 1
    )
    THEN RAISE EXCEPTION 'A menu item must be one of Main, Side, or Dessert';
    END IF;
    RETURN NULL;
END;
$menuTotalParticipation$ LANGUAGE plpgsql;

CREATE CONSTRAINT TRIGGER Trigger_MenuItem_Main
AFTER INSERT OR UPDATE OR DELETE ON Main
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE PROCEDURE menuTotalParticipation();

CREATE CONSTRAINT TRIGGER Trigger_MenuItem_Side
AFTER INSERT OR UPDATE OR DELETE ON Side
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE PROCEDURE menuTotalParticipation();

CREATE CONSTRAINT TRIGGER Trigger_MenuItem_Dessert
AFTER INSERT OR UPDATE OR DELETE ON Dessert
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE PROCEDURE menuTotalParticipation();

-- menuitem must be in one of main, side, dessert
CREATE OR REPLACE FUNCTION menuItemTotalParticipation()
  RETURNS TRIGGER AS $menuItemTotalParticipation$
BEGIN
    IF new.menuItemId NOT IN (
        SELECT menuItemId FROM Main
        UNION ALL
        SELECT menuItemId FROM Side
        UNION ALL
        SELECT menuItemId FROM Dessert
    )
    THEN RAISE EXCEPTION 'A menu item must belong to Main, Side, or Dessert';
    END IF;
    RETURN NULL;
END;
$menuItemTotalParticipation$ LANGUAGE plpgsql;

CREATE CONSTRAINT TRIGGER Trigger_MenuItem
AFTER INSERT OR UPDATE OR DELETE ON MenuItem
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE PROCEDURE menuItemTotalParticipation();




----------- Insert Rows --------------------
BEGIN;
    INSERT INTO MenuItem(menuItemId, name, price, description)
    VALUES (1, 'Air', 100.00, 'Organic and fresh');
    INSERT INTO Main(menuItemId) VALUES (1);

    INSERT INTO MenuItem(menuItemId, name, price, description)
    VALUES (2, 'Water', 99.00, 'Organic and fresh');
    INSERT INTO Side(menuItemId) VALUES (2);

    INSERT INTO MenuItem(menuItemId, name, price, description)
    VALUES (3, 'Love', 100000.00, 'Not free');
    INSERT INTO Dessert(menuItemId) VALUES (3);

    INSERT INTO MenuItem(menuItemId, name, price, description)
    VALUES (4, 'Dust', 100000.00, 'Grade A Dust');
    INSERT INTO Main(menuItemId) VALUES (4);

    INSERT INTO Menu(menuId, description) VALUES (1, 'Basic Menu');
    INSERT INTO Contains(menuId, menuItemId) VALUES (1, 1);
COMMIT;


INSERT INTO Staff(staffid, position, name)
VALUES (1, 'General Manager', 'Generic Name');
INSERT INTO Customer(customerId, firstName, lastName, address, mobileNo)
VALUES (1, 'Average', 'Joe', 'Not Earth', '0456123456');
INSERT INTO Courier(courierId, name, address, mobile)
VALUES (1, 'TheFirstCoutier', 'Generic Address of Courier', '0432123456');
INSERT INTO Delivery(deliveryId, courierId, timeReady, timeDelivered)
VALUES (1, 1, CURRENT_TIMESTAMP - interval '2 hour', CURRENT_TIMESTAMP);
INSERT INTO "Order"(orderId, customerId, staffId, deliveryId, totalCharge)
VALUES (1, 1, 1, 1, 112.98);
INSERT INTO OrderItem(orderItemId, orderId, customerId, menuItemId, quantity, charge)
VALUES (1, 1, 1, 1, 2, 100);

BEGIN;
    -- populate Courier table
    INSERT INTO Courier(courierId, name, address, mobile)
    VALUES (2, 'Courier 2', 'Generic Address of Courier', '0432342156'),
           (3, 'Courier 3', 'Generic Address of Courier', '0432145236'),
           (4, 'Courier 4', 'Generic Address of Courier', '0314345126'),
           (5, 'Courier 5', 'Generic Address of Courier', '0433424152'),
           (6, 'Courier 6', 'Generic Address of Courier', '0415632231');

    -- populate Delivery table
    INSERT INTO Delivery(deliveryId, courierId, timeReady, timeDelivered)
    VALUES (2, 2, CURRENT_TIMESTAMP - interval '2 hour', CURRENT_TIMESTAMP),
           (3, 4, CURRENT_TIMESTAMP - interval '1 hour', CURRENT_TIMESTAMP),
           (4, 5, CURRENT_TIMESTAMP - interval '4 hour', CURRENT_TIMESTAMP),
           (5, 2, CURRENT_TIMESTAMP - interval '3 hour', CURRENT_TIMESTAMP),
           (6, 6, CURRENT_TIMESTAMP - interval '23 hour', CURRENT_TIMESTAMP);

    -- populate Customer table
    INSERT INTO Customer(customerId, firstName, lastName, address, mobileNo)
    VALUES (2, 'Average', 'Karen', 'Not Earth', '0456123456'),
           (3, 'Geoffrey', 'Hinton', 'Not Earth', '0456123456'),
           (4, 'Alan', 'Turing', 'Not Earth', '0456123456'),
           (5, 'Ada', 'Lovelace', 'Not Earth', '0456123456'),
           (6, 'Grace', 'Hopper', 'Not Earth', '0456123456');

    -- populate Order table
    INSERT INTO "Order"(orderId, customerId, staffId, deliveryId, totalCharge)
    VALUES (2, 1, 1, 5, 68.50),
           (3, 5, 1, 3, 20.00),
           (4, 6, 1, 2, 750.01),
           (3, 3, 1, 1, 324.92);

    -- populate OrderItem table
    INSERT INTO OrderItem(orderItemId, orderId, customerId, menuItemId, quantity, charge)
    VALUES (3, 2, 1, 4, 3, 122),
           (4, 3, 5, 2, 4, 324),
           (5, 4, 6, 1, 1, 10),
           (6, 3, 3, 3, 2, 24);
COMMIT;
