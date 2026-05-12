--This query calculates payment processing time from creation to completion.
 --It helps identify slow payments and potential performance issues in asynchronous processing.
SELECT
    payment_id,
    status,
    created_at,
    completed_at,
    dateDiff('second', created_at, completed_at) AS processing_seconds
FROM qa_lab.payments
WHERE completed_at IS NOT NULL
ORDER BY processing_seconds DESC;