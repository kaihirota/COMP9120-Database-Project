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
    CONSTRAINT FK_menuItemId_Main FOREIGN KEY (menuItemId) REFERENCES MenuItem ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE Side(
    menuItemId INTEGER PRIMARY KEY,
    CONSTRAINT FK_menuItemId_Side FOREIGN KEY (menuItemId) REFERENCES MenuItem ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE Dessert(
    menuItemId INTEGER PRIMARY KEY,
    CONSTRAINT FK_menuItemId_Dessert FOREIGN KEY (menuItemId) REFERENCES MenuItem ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
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
    CONSTRAINT FK_courierId_Delivery FOREIGN KEY (courierId) REFERENCES Courier ON UPDATE CASCADE,
    CONSTRAINT CK_timeConflict_Delivery CHECK(timeReady < timeDelivered)
);
CREATE TABLE Contains(
    menuId INTEGER,
    menuItemId INTEGER,
    PRIMARY KEY (menuId, menuItemId),
    CONSTRAINT FK_menuId_Contains FOREIGN KEY (menuId) REFERENCES Menu (menuId) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT FK_menuItemId_Contains FOREIGN KEY (menuItemId) REFERENCES MenuItem (menuItemId) ON UPDATE CASCADE ON DELETE CASCADE
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
    CONSTRAINT FK_customerId_Order FOREIGN KEY (customerId) REFERENCES Customer ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT FK_staffId_Order FOREIGN KEY (staffId) REFERENCES Staff ON UPDATE CASCADE,
    CONSTRAINT FK_deliveryId_Order FOREIGN KEY (deliveryId) REFERENCES Delivery ON UPDATE CASCADE,
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
    CONSTRAINT FK_orderId_OrderItem FOREIGN KEY (orderId, customerId) REFERENCES "Order" ON UPDATE CASCADE ON DELETE CASCADE,

    -- Doesn't delete on cascade because even if menuitems get deleted, it
    -- wouldn't be ideal to lose past transactions
    CONSTRAINT FK_menuItemId_OrderItem FOREIGN KEY (menuItemId) REFERENCES MenuItem ON UPDATE CASCADE,
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
CREATE OR REPLACE FUNCTION menuTotalParticipation() RETURNS TRIGGER AS $menuTotalParticipation$
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
CREATE OR REPLACE FUNCTION menuItemTotalParticipation() RETURNS TRIGGER AS $menuItemTotalParticipation$
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
