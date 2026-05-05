SELECT
    status,
    count() AS payments_count
FROM qa_lab.payments
GROUP BY status
ORDER BY payments_count DESC;