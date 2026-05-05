/*SELECT
    payment_id,
    user_id,
    currency,
    amount,
    status,
    created_at,
    updated_at,
    dateDiff('minute', updated_at, now()) AS minutes_without_update
FROM qa_lab.payments
WHERE status IN ('created', 'pending', 'processing')
  AND updated_at < now() - INTERVAL 15 MINUTE
ORDER BY minutes_without_update DESC;*/
CREATE VIEW qa_lab.v_stuck_payments AS
SELECT
    payment_id,
    user_id,
    status,
    updated_at,
    dateDiff('minute', updated_at, now()) AS minutes_without_update
FROM qa_lab.payments
WHERE status IN ('created', 'pending', 'processing')
  AND updated_at < now() - INTERVAL 15 MINUTE;
