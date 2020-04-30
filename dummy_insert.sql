BEGIN;
    INSERT INTO Staff(staffid, position, name) VALUES (1, 'General Manager', 'Generic Name');

    INSERT INTO MenuItem(menuItemId, name, price, description) VALUES (1, 'Air', 100.00, 'Organic and fresh');
    INSERT INTO MenuItem(menuItemId, name, price, description) VALUES (2, 'Water', 99.00, 'Organic and fresh');
    INSERT INTO MenuItem(menuItemId, name, price, description) VALUES (3, 'Love', 100000.00, 'Not free');

    INSERT INTO Main(menuItemId) VALUES (1);
    INSERT INTO Side(menuItemId) VALUES (2);
    INSERT INTO Dessert(menuItemId) VALUES (3);

    INSERT INTO Contains(menuId, menuItemId) VALUES (1, 1);
    INSERT INTO Menu(menuId, description) VALUES (1, 'Basic Menu');

    INSERT INTO Customer(customerId, firstName, lastName, address, mobileNo) VALUES (1, 'Average', 'Joe', 'Not Earth', '0456123456');
    INSERT INTO Courier(courierId, name, address, mobile) VALUES (1, 'TheFirstCoutier', 'Generic Address of Courier', '0432123456');
    INSERT INTO Delivery(deliveryId, courierId, timeReady, timeDelivered) VALUES (1, 1, CURRENT_TIMESTAMP - interval '2 hour', CURRENT_TIMESTAMP);
    INSERT INTO "Order"(orderId, customerId, staffId, deliveryId, totalCharge) VALUES (1, 1, 1, 1, 112.98);
    INSERT INTO OrderItem(orderItemId, orderId, customerId, menuItemId, quantity, charge) VALUES (1, 1, 1, 1, 2, 100);
    -- done
    -- check that duplicates not allowed in 3 tables
    -- check that i can't insert into 3 tables when it doesn't exist in menuItem
    -- can insert into 3 subtables before inserting into menuitem, but must satisfy constraint by end of transaction
COMMIT;
