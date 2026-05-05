SELECT
    currency,
    count() AS payments_count,
    sum(amount) AS total_amount
FROM qa_lab.payments
GROUP BY currency
ORDER BY total_amount DESC;