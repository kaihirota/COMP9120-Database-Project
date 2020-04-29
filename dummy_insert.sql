INSERT INTO Staff(staffid, position, name) VALUES (1, 'General Manager', 'Generic Name');
INSERT INTO Menu(menuId, description) VALUES (1, 'Basic Menu');
INSERT INTO MenuItem(menuItemId, name, price, description, isA) VALUES (1, 'Air', 100.00, 'Organic and fresh', 'Main');
INSERT INTO Customer(customerId, firstName, lastName, address, mobileNo) VALUES (1, 'Average', 'Joe', 'Not Earth', '0456123456');
INSERT INTO Courier(courierId, name, address, mobile) VALUES (1, 'TheFirstCoutier', 'Generic Address of Courier', '0432123456');
INSERT INTO Delivery(deliveryId, courierId, timeReady, timeDelivered) VALUES (1, 1, CURRENT_TIMESTAMP - interval '2 hour', CURRENT_TIMESTAMP);
INSERT INTO Contains(menuId, menuItemId) VALUES (1, 1);
INSERT INTO "Order"(orderId, customerId, staffId, deliveryId, totalCharge) VALUES (1, 1, 1, 1, 112.98);
INSERT INTO OrderItem(orderItemId, orderId, customerId, menuItemId, quantity, charge) VALUES (1, 1, 1, 1, 2, 100);
