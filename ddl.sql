-- 1. Fields in a tuple related to dates and times should always have values.
-- 2. All fields in a tuple relating to details about a name (eg: Menu Item Name, First Name, etc) should always have a value.
-- 4. Customers must have a specified mobile number.

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
    CONSTRAINT FK_menuItemId_Main FOREIGN KEY (menuItemId) REFERENCES MenuItem DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE Side(
    menuItemId INTEGER PRIMARY KEY,
    CONSTRAINT FK_menuItemId_Side FOREIGN KEY (menuItemId) REFERENCES MenuItem DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE Dessert(
    menuItemId INTEGER PRIMARY KEY,
    CONSTRAINT FK_menuItemId_Dessert FOREIGN KEY (menuItemId) REFERENCES MenuItem DEFERRABLE INITIALLY DEFERRED
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
    CONSTRAINT FK_menuId_Contains FOREIGN KEY (menuId) REFERENCES Menu (menuId) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT FK_menuItemId_Contains FOREIGN KEY (menuItemId) REFERENCES MenuItem (menuItemId) ON DELETE CASCADE
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
    menuItemId INTEGER NOT NULL,
    customerId INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    charge NUMERIC(10, 2) NOT NULL,
    CONSTRAINT FK_orderId_OrderItem FOREIGN KEY (orderId) REFERENCES "Order" ON DELETE CASCADE,
    CONSTRAINT FK_customerId_OrderItem FOREIGN KEY (customerId) REFERENCES Customer, -- ON DELETE CASCADE?
    CONSTRAINT FK_menuItemId_OrderItem FOREIGN KEY (menuItemId) REFERENCES MenuItem, -- ON DELETE CASCADE?
    CONSTRAINT CK_quantity_OrderItem CHECK(quantity > 0)
    -- add check - ensure order and order item matches
    -- what about item price and order match? check that too?
);


-- menu must have at least 1 item
CREATE OR REPLACE FUNCTION menuTotalParticipation() RETURNS TRIGGER AS $menuTotalParticipation$
BEGIN
    IF new.menuId NOT IN (
        SELECT menuId FROM Contains
    )
    THEN RAISE EXCEPTION 'Menu must contain at least 1 item prior to insertion';
    END IF;
    IF (new.menuId IN (
        SELECT menuId FROM Contains
    )) THEN RETURN NEW;
    END IF;
END;
$menuTotalParticipation$ LANGUAGE plpgsql;

CREATE CONSTRAINT TRIGGER Trigger_MenuContains
AFTER INSERT OR UPDATE OR DELETE ON Menu
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE PROCEDURE menuTotalParticipation();

  -- check that each row of menuitem is in main, side, dessert
  -- make sure menuitem cannot be in more than 1 of the 3 tables
  -- CREATE OR REPLACE FUNCTION MenuItemDisjointTotalParticipation() RETURNS TRIGGER AS $MenuItemDisjointTotalParticipation$
  --     BEGIN
  --         IF new.menuItemId NOT IN (
  --             SELECT * FROM Main
  --         	UNION ALL
  --         	SELECT * FROM Side
  --         	UNION ALL
  --         	SELECT * FROM Dessert
  --         ) THEN RAISE EXCEPTION 'Menu items must exist in Main, Side, or Dessert before being inserted to MenuItem table';
  --         END IF;
  --         -- RETURN NEW;
  --         RETURN NULL;
  --     END;
  -- $MenuItemDisjointTotalParticipation$ LANGUAGE plpgsql;
  --
  -- CREATE TRIGGER Trigger_MenuItem
  --     BEFORE INSERT OR UPDATE ON menuItem
  --     FOR EACH STATEMENT EXECUTE PROCEDURE MenuItemDisjointTotalParticipation();



-- TODO this is not tested
-- menu must have at least 1 item
-- CREATE OR REPLACE FUNCTION menuTotalParticipation() RETURNS TRIGGER AS $menuTotalParticipation$
-- BEGIN
  -- IF (new.MenuId not in (select MenuId from Contains)) THEN
    -- Raise exception 'Menuitem needed';
  -- END IF;
  -- RETURN NULL;
-- END;
-- $menuTotalParticipation$ LANGUAGE plpgsql;
--
-- -- triggers
-- CREATE TRIGGER MenuContainsTotalParticipation
    -- AFTER INSERT OR UPDATE OR DELETE ON Contains
    -- FOR EACH STATEMENT EXECUTE PROCEDURE menuTotalParticipation();
--
-- -- triggers
-- CREATE TRIGGER MenuContainsTotalParticipation
    -- AFTER INSERT OR UPDATE OR DELETE ON Contains
    -- FOR EACH STATEMENT EXECUTE PROCEDURE menuTotalParticipation();
-- CREATE CONSTRAINT TRIGGER Trigger_MenuContains
-- AFTER INSERT OR UPDATE OR DELETE ON Menu
-- DEFERRABLE INITIALLY DEFERRED
-- FOR EACH ROW EXECUTE PROCEDURE menuTotalParticipation();
--
-- check that each row of menuitem is in main, side, dessert
-- make sure menuitem cannot be in more than 1 of the 3 tables
-- CREATE OR REPLACE FUNCTION MenuItemDisjointTotalParticipation() RETURNS TRIGGER AS $MenuItemDisjointTotalParticipation$
--     BEGIN
--         IF new.menuItemId NOT IN (
--             SELECT * FROM Main
--         	UNION ALL
--         	SELECT * FROM Side
--         	UNION ALL
--         	SELECT * FROM Dessert
--         ) THEN RAISE EXCEPTION 'Menu items must exist in Main, Side, or Dessert before being inserted to MenuItem table';
--         END IF;
--         -- RETURN NEW;
--         RETURN NULL;
--     END;
-- $MenuItemDisjointTotalParticipation$ LANGUAGE plpgsql;
--
-- CREATE TRIGGER Trigger_MenuItem
--     BEFORE INSERT OR UPDATE ON menuItem
--     FOR EACH STATEMENT EXECUTE PROCEDURE MenuItemDisjointTotalParticipation();
