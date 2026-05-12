--This check validates financial consistency. For every transaction and currency, total debit should match total credit.
--If there is a difference, it may indicate accounting inconsistency or incorrect ledger posting.
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