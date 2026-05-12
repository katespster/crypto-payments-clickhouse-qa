--This is one of the most important checks. It detects mismatch between provider status and internal status. If the provider has confirmed the transaction, but our internal
--payment is still not completed or settled, it may indicate callback processing failure or status synchronization bug.
SELECT
    p.payment_id,
    p.user_id,
    p.status AS internal_status,
    c.provider_status,
    c.tx_hash,
    p.updated_at,
    c.received_at
FROM qa_lab.payments AS p
INNER JOIN qa_lab.provider_callbacks AS c
    ON p.payment_id = c.payment_id
WHERE c.provider_status = 'confirmed'
  AND p.status NOT IN ('completed', 'settled');