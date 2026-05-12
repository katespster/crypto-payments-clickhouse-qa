-- This query is used for reconciliation between internal payment status and provider callback status.
-- It helps verify that callbacks are received and linked to the correct payment.
SELECT
    p.payment_id,
    p.status AS internal_status,
    c.provider_status,
    c.tx_hash,
    c.received_at
FROM qa_lab.payments AS p
INNER JOIN qa_lab.provider_callbacks AS c
    ON p.payment_id = c.payment_id
LIMIT 20;