-- Executed only when the PostgreSQL volume is first initialized.
CREATE SCHEMA sales;
CREATE TABLE sales.customers (
    id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    region TEXT NOT NULL
);
INSERT INTO sales.customers VALUES
    (101, 'An', 'Ha Noi'), (102, 'Binh', 'Da Nang'), (103, 'Chi', 'TP HCM');
CREATE TABLE sales.orders (
    id BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES sales.customers(id),
    amount NUMERIC(12,2) NOT NULL,
    status TEXT NOT NULL
);
INSERT INTO sales.orders VALUES
    (1, 101, 120000.00, 'paid'),
    (2, 102, 250000.00, 'paid'),
    (3, 101,  80000.00, 'pending');
COMMENT ON TABLE sales.orders IS 'Orders created directly in PostgreSQL before catalog registration';
