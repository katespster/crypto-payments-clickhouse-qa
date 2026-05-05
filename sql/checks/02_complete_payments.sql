SELECT
    payment_id,
    user_id,
    amount,
    currency,
    status
FROM qa_lab.payments
WHERE status = 'completed';