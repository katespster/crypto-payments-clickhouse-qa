SELECT
    payment_id,
    status,
    created_at,
    completed_at,
    dateDiff('second', created_at, completed_at) AS processing_seconds
FROM qa_lab.payments
WHERE completed_at IS NOT NULL
ORDER BY processing_seconds DESC;