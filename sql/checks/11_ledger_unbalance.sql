SELECT
    transaction_id,
    currency,
    round(sumIf(amount, entry_type = 'debit'), 8) AS total_debit,
    round(sumIf(amount, entry_type = 'credit'), 8) AS total_credit,
    round(total_debit - total_credit, 8) AS diff
FROM qa_lab.ledger_entries
GROUP BY
    transaction_id,
    currency
HAVING abs(diff) > 0.00000001
ORDER BY abs(diff) DESC;