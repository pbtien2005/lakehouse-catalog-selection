SELECT c.name, COUNT(*) AS orders, SUM(o.amount) AS revenue
FROM sales.orders o JOIN sales.customers c ON o.customer_id = c.id
WHERE o.status = 'paid'
GROUP BY c.name ORDER BY c.name;
