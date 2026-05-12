--This check validates payment state transitions. I use a window function to compare current and previous statuses for each payment.
 --If a payment moves from failed to completed, it may indicate an invalid state transition or race condition.
WITH ordered_events AS
(
    SELECT
        payment_id,
        event_time,
        new_status,
        lagInFrame(new_status) OVER (
            PARTITION BY payment_id
            ORDER BY event_time
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS previous_status
    FROM qa_lab.payment_events
)
SELECT
    payment_id,
    previous_status,
    new_status,
    event_time
FROM ordered_events
WHERE previous_status = 'failed'
  AND new_status = 'completed';