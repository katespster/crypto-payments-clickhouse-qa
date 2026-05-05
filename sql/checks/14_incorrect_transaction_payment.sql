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