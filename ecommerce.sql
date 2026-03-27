--1.what is the overall business performance?
SELECT 
    COUNT(DISTINCT "InvoiceNo") as total_orders,
    COUNT(DISTINCT "CustomerID") as total_customers,
    SUM("TotalPrice") as total_revenue,
    ROUND(AVG("TotalPrice")::numeric, 2) as avg_order_value
FROM transactions;




-- Fix InvoiceDate column type
ALTER TABLE transactions 
ALTER COLUMN "InvoiceDate" TYPE timestamp 
USING "InvoiceDate"::timestamp;

-- Fix TotalPrice column type (if needed)
ALTER TABLE transactions 
ALTER COLUMN "TotalPrice" TYPE numeric 
USING "TotalPrice"::numeric;

--2.How many active vs new customers?
WITH customer_first_purchase AS (
    SELECT 
        "CustomerID",
        MIN("InvoiceDate") as first_purchase
    FROM transactions
    GROUP BY "CustomerID"
)
SELECT 
    COUNT(DISTINCT t."CustomerID") as active_customers_2011,
    COUNT(DISTINCT CASE 
        WHEN EXTRACT(YEAR FROM c.first_purchase) = 2011 
        THEN t."CustomerID" 
    END) as new_customers_2011
FROM transactions t
JOIN customer_first_purchase c ON t."CustomerID" = c."CustomerID"
WHERE EXTRACT(YEAR FROM t."InvoiceDate") = 2011;


--3.monthly sales trend
SELECT 
    DATE_TRUNC('month', "InvoiceDate") as month,
    COUNT(DISTINCT "InvoiceNo") as orders,
    COUNT(DISTINCT "CustomerID") as unique_customers,
    SUM("Quantity") as items_sold,
    SUM("TotalPrice") as revenue,
    ROUND(AVG("TotalPrice")::numeric, 2) as avg_order_value
FROM transactions
GROUP BY DATE_TRUNC('month', "InvoiceDate")
ORDER BY month;















--4.top countries by revenue
SELECT 
    "Country",
    COUNT(DISTINCT "InvoiceNo") as orders,
    COUNT(DISTINCT "CustomerID") as customers,
    SUM("TotalPrice") as revenue,
    ROUND(AVG("TotalPrice")::numeric, 2) as avg_order_value,
    ROUND((100.0 * SUM("TotalPrice") / SUM(SUM("TotalPrice")) OVER ())::numeric, 2) as revenue_percentage
FROM transactions
GROUP BY "Country"
HAVING SUM("TotalPrice") > 0
ORDER BY revenue DESC
LIMIT 15;

--5.What days of week have highest sales?
SELECT 
    "DayOfWeek",
    COUNT(*) as days_count,
    ROUND(AVG("Revenue")::numeric, 2) as avg_daily_revenue,
    ROUND(AVG("Order")::numeric, 2) as avg_daily_orders,  -- Note: "Order" not "Orders"
    SUM("Revenue") as total_revenue
FROM features_daily_sales
GROUP BY "DayOfWeek"
ORDER BY 
    CASE "DayOfWeek"
        WHEN 'Monday' THEN 1
        WHEN 'Tuesday' THEN 2
        WHEN 'Wednesday' THEN 3
        WHEN 'Thursday' THEN 4
        WHEN 'Friday' THEN 5
        WHEN 'Saturday' THEN 6
        WHEN 'Sunday' THEN 7
    END;
	
	
--6. top 20 best selling products
SELECT 
    "StockCode",
    MAX("Description") as product_description,
    COUNT(DISTINCT "InvoiceNo") as times_ordered,
    SUM("Quantity") as total_quantity_sold,
    SUM("TotalPrice") as total_revenue,
    ROUND(AVG("UnitPrice")::numeric, 2) as avg_price
FROM transactions
WHERE "Description" != 'Unknown'
GROUP BY "StockCode"
ORDER BY total_quantity_sold DESC
LIMIT 20;












--7.products with highest average order value
SELECT 
    "StockCode",
    MAX("Description") as product_description,
    ROUND(AVG("TotalPrice")::numeric, 2) as avg_transaction_value,
    COUNT(*) as times_sold,
    SUM("Quantity") as total_units
FROM transactions
GROUP BY "StockCode"
HAVING COUNT(*) > 10
ORDER BY avg_transaction_value DESC
LIMIT 20;

--8. products often bought together
SELECT 
    t1."StockCode" as product1,
    t2."StockCode" as product2,
    COUNT(*) as times_bought_together
FROM transactions t1
JOIN transactions t2 ON t1."InvoiceNo" = t2."InvoiceNo" 
    AND t1."StockCode" < t2."StockCode"
GROUP BY t1."StockCode", t2."StockCode"
ORDER BY times_bought_together DESC
LIMIT 30;



















--9. customer segments distribution
SELECT 
    s."Segment",
    COUNT(*) as customer_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage,
    ROUND(AVG(v."predicted_clv")::numeric, 2) as avg_predicted_value
FROM customer_segments s
LEFT JOIN clv_predictions v ON s."CustomerID" = v."CustomerID"
GROUP BY s."Segment"
ORDER BY avg_predicted_value DESC;

--10. customer value distribution
SELECT 
    "value_category",
    COUNT(*) as customer_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage,
    ROUND(MIN("predicted_clv")::numeric, 2) as min_clv,
    ROUND(AVG("predicted_clv")::numeric, 2) as avg_clv,
    ROUND(MAX("predicted_clv")::numeric, 2) as max_clv,
    ROUND(SUM("predicted_clv")::numeric, 2) as total_value
FROM clv_predictions
GROUP BY "value_category"
ORDER BY 
    CASE "value_category"
        WHEN 'VIP' THEN 1
        WHEN 'High Value' THEN 2
        WHEN 'Medium Value' THEN 3
        WHEN 'Low Value' THEN 4
    END;
	
--11. top 20 most valuable customers
SELECT 
    c."CustomerID",
    s."Segment",
    c."value_category",
    ROUND(c."predicted_clv"::numeric, 2) as predicted_value,
    COUNT(DISTINCT t."InvoiceNo") as actual_orders,
    SUM(t."Quantity") as actual_items,
    ROUND(SUM(t."TotalPrice")::numeric, 2) as actual_spent
FROM clv_predictions c
JOIN customer_segments s ON c."CustomerID" = s."CustomerID"
JOIN transactions t ON c."CustomerID" = t."CustomerID"
GROUP BY c."CustomerID", s."Segment", c."value_category", c."predicted_clv"
ORDER BY c."predicted_clv" DESC
LIMIT 20;

--12. average customer lifetime by segment
WITH customer_lifetime AS (
    SELECT 
        t."CustomerID",
        MIN(t."InvoiceDate"::timestamp) as first_purchase,
        MAX(t."InvoiceDate"::timestamp) as last_purchase,
        EXTRACT(DAY FROM MAX(t."InvoiceDate"::timestamp) - MIN(t."InvoiceDate"::timestamp)) as lifespan_days
    FROM transactions t
    GROUP BY t."CustomerID"
    HAVING COUNT(DISTINCT t."InvoiceNo") > 1
)
SELECT 
    s."Segment",
    COUNT(*) as customer_count,
    ROUND(AVG(l.lifespan_days)::numeric, 2) as avg_lifespan_days,
    ROUND(AVG(l.lifespan_days/30.0)::numeric, 2) as avg_lifespan_months,
    MAX(l.lifespan_days) as max_lifespan_days
FROM customer_lifetime l
JOIN customer_segments s ON l."CustomerID" = s."CustomerID"
GROUP BY s."Segment"
ORDER BY avg_lifespan_days DESC;

--13. customer retention rate
WITH monthly_customers AS (
    SELECT 
        DATE_TRUNC('month', "InvoiceDate"::timestamp) as month,
        "CustomerID"
    FROM transactions
    GROUP BY DATE_TRUNC('month', "InvoiceDate"::timestamp), "CustomerID"
),
retention AS (
    SELECT 
        current.month,
        COUNT(DISTINCT current."CustomerID") as current_customers,
        COUNT(DISTINCT prev."CustomerID") as retained_customers
    FROM monthly_customers current
    LEFT JOIN monthly_customers prev 
        ON current."CustomerID" = prev."CustomerID"
        AND prev.month = current.month - INTERVAL '1 month'
    GROUP BY current.month
)
SELECT 
    TO_CHAR(month, 'YYYY-MM') as month,
    current_customers,
    retained_customers,
    ROUND(100.0 * retained_customers / NULLIF(current_customers, 0), 2) as retention_rate
FROM retention
ORDER BY month;

--14. rfm patterns by segment
SELECT 
    s."Segment",
    COUNT(*) as customer_count,
    ROUND(AVG(v."predicted_clv")::numeric, 2) as avg_predicted_clv,
    MIN(v."predicted_clv") as min_clv,
    MAX(v."predicted_clv") as max_clv
FROM customer_segments s
LEFT JOIN clv_predictions v ON s."CustomerID" = v."CustomerID"
GROUP BY s."Segment"
ORDER BY avg_predicted_clv DESC;

--15. customers most likely to churn
SELECT 
    s."CustomerID",
    s."Segment",
    MAX(t."InvoiceDate"::timestamp) as last_purchase_date,
    EXTRACT(DAY FROM CURRENT_DATE - MAX(t."InvoiceDate"::timestamp)) as days_since_last_purchase,
    COUNT(DISTINCT t."InvoiceNo") as total_orders,
    SUM(t."TotalPrice") as total_spent
FROM customer_segments s
JOIN transactions t ON s."CustomerID" = t."CustomerID"
WHERE s."Segment" = 'At-Risk Customers'
GROUP BY s."CustomerID", s."Segment"
HAVING MAX(t."InvoiceDate"::timestamp) < CURRENT_DATE - INTERVAL '60 days'
ORDER BY days_since_last_purchase DESC
LIMIT 20;





















