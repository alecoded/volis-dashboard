SELECT 
    s.seller_id,
    s.seller_city,
    s.seller_state,
    sum(i.price) as faturamento_vendedor,
    count(i.order_id) as total_vendas
FROM {{ ref('olist_sellers_dataset') }} s
JOIN {{ ref('olist_order_items_dataset') }} i ON s.seller_id = i.seller_id
GROUP BY 1, 2, 3
ORDER BY 4 DESC
LIMIT 100