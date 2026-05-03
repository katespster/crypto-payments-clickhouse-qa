CREATE TABLE IF NOT EXISTS qa_lab.payments
(
    payment_id UUID,
    user_id UInt64,
    idempotency_key String,
    provider LowCardinality(String),
    currency LowCardinality(String),
    amount Decimal(18, 8),
    status LowCardinality(String),
    created_at DateTime,
    updated_at DateTime,
    completed_at Nullable(DateTime)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(created_at)
ORDER BY (created_at, provider, currency, payment_id);


CREATE TABLE IF NOT EXISTS qa_lab.payment_events
(
    event_id UUID,
    payment_id UUID,
    event_type LowCardinality(String),
    old_status LowCardinality(String),
    new_status LowCardinality(String),
    event_time DateTime,
    source LowCardinality(String)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(event_time)
ORDER BY (payment_id, event_time);


CREATE TABLE IF NOT EXISTS qa_lab.provider_callbacks
(
    callback_id UUID,
    payment_id UUID,
    provider LowCardinality(String),
    provider_status LowCardinality(String),
    tx_hash Nullable(String),
    blockchain_network LowCardinality(String),
    received_at DateTime
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(received_at)
ORDER BY (provider, received_at, payment_id);


CREATE TABLE IF NOT EXISTS qa_lab.ledger_entries
(
    entry_id UUID,
    transaction_id UUID,
    payment_id UUID,
    user_id UInt64,
    currency LowCardinality(String),
    entry_type LowCardinality(String),
    amount Decimal(18, 8),
    created_at DateTime
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(created_at)
ORDER BY (created_at, currency, transaction_id);