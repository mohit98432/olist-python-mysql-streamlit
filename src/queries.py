"""Business queries for order-line analytics, tied to the Olist SQL schema."""

ORDER_LINES = """
SELECT o.order_id, c.customer_id, c.customer_unique_id, c.state,
       o.order_date, o.order_status, i.item_number, i.product_id,
       p.product_name, cat.category_name AS category,
       i.quantity, i.unit_price, i.discount_amount,
       (i.quantity * i.unit_price - i.discount_amount) AS line_revenue
FROM orders AS o
JOIN customers AS c ON c.customer_id = o.customer_id
JOIN order_items AS i ON i.order_id = o.order_id
JOIN products AS p ON p.product_id = i.product_id
JOIN categories AS cat ON cat.category_id = p.category_id
WHERE o.order_date >= :start_date AND o.order_date < :end_date
ORDER BY o.order_date, o.order_id, i.item_number
"""

SHIPMENTS = """
SELECT o.order_id, s.shipped_at, s.delivered_at, s.estimated_delivery
FROM orders o JOIN shipments s ON s.order_id=o.order_id
WHERE o.order_date >= :start_date AND o.order_date < :end_date
"""
