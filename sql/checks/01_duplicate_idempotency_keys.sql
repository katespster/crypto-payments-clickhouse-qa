SELECT
    idempotency_key,
    count() AS cnt,
    groupArray(payment_id) AS payment_ids,
    groupArray(status) AS statuses
FROM qa_lab.payments
WHERE created_at >= now() - INTERVAL 1 DAY
GROUP BY idempotency_key
HAVING cnt > 1
ORDER BY cnt DESC;