SELECT
    currency,
    count() AS total,
    countIf(status = 'completed') AS completed_count,
    countIf(status = 'processing') AS processing_count,
    sumIf(amount, status = 'completed') AS completed_amount
FROM qa_lab.payments
GROUP BY currency
ORDER BY total DESC;