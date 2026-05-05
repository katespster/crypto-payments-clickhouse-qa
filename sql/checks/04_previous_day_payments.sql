SELECT
    payment_id,
    status,
    created_at
FROM qa_lab.payments
WHERE created_at >= now() - INTERVAL 1 DAY;