SELECT 
    p.product_category_name,
    avg(r.review_score) as nota_media,
    count(r.review_id) as total_avaliacoes
FROM {{ ref('olist_order_reviews_dataset') }} r
JOIN {{ ref('olist_order_items_dataset') }} i ON r.order_id = i.order_id
JOIN {{ ref('olist_products_dataset') }} p ON i.product_id = p.product_id
GROUP BY 1
ORDER BY 2 DESC