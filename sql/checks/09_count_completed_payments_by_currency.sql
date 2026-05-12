--This query uses conditional aggregation. I can compare total payments, completed payments, processing payments and completed amount per currency.
--It helps detect if some currency has abnormal processing rate or too many unfinished payments.
SELECT
    currency,
    count() AS total,
    countIf(status = 'completed') AS completed_count,
    countIf(status = 'processing') AS processing_count,
    sumIf(amount, status = 'completed') AS completed_amount
FROM qa_lab.payments
GROUP BY currency
ORDER BY total DESC;