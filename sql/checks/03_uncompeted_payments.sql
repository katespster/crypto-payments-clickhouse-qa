SELECT
    payment_id,
    status,
    updated_at
FROM qa_lab.payments
WHERE status IN ('created', 'pending', 'processing');