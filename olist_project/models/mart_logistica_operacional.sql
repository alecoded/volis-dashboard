SELECT 
    order_status,
    count(order_id) as total_pedidos,
    avg(date_diff('day', cast(order_purchase_timestamp as timestamp), cast(order_delivered_customer_date as timestamp))) as tempo_medio_entrega_dias
FROM {{ ref('olist_orders_dataset') }}
WHERE order_delivered_customer_date IS NOT NULL
GROUP BY 1