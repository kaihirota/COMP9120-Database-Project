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
