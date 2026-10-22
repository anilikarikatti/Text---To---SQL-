INSERT INTO customers (name, email, city) VALUES
('Ananya Rao', 'ananya@example.com', 'Chennai'),
('Rahul Sharma', 'rahul@example.com', 'Bengaluru'),
('Priya Nair', 'priya@example.com', 'Chennai'),
('Vikram Patel', 'vikram@example.com', 'Mumbai'),
('Sara Khan', 'sara@example.com', 'Hyderabad');

INSERT INTO products (name, category) VALUES
('Laptop', 'Electronics'),
('Mouse', 'Electronics'),
('Office Chair', 'Furniture'),
('Office Desk', 'Furniture');

INSERT INTO orders (customer_id, order_date, status) VALUES
(1, '2026-01-10', 'completed'),
(2, '2026-01-15', 'completed'),
(1, '2026-02-02', 'completed'),
(3, '2026-02-10', 'cancelled'),
(4, '2026-02-12', 'completed'),
(5, '2026-03-01', 'pending'),
(2, '2026-03-05', 'completed'),
(3, '2026-03-08', 'completed');

INSERT INTO order_items
    (order_id, product_id, quantity, unit_price)
VALUES
(1, 1, 1, 70000.00),
(1, 2, 2,   500.00),
(2, 1, 1, 68000.00),
(3, 3, 2,  8000.00),
(4, 4, 1, 12000.00),
(5, 1, 1, 72000.00),
(5, 3, 1,  7500.00),
(6, 4, 2, 11000.00),
(7, 2, 3,   450.00),
(8, 3, 1,  8000.00),
(8, 4, 1, 15000.00);



