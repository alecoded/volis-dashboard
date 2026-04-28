SELECT 
    date_trunc('month', cast(o.order_purchase_timestamp as timestamp)) as mes,
    sum(p.payment_value) as faturamento_total,
    count(o.order_id) as volume_pedidos
FROM olist_orders_dataset o
JOIN olist_order_payments_dataset p ON o.order_id = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY 1