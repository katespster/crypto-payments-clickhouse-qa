from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from uuid import uuid4
import json
import random

import clickhouse_connect


PROVIDER = "mock_crypto_provider"
NETWORK = "ETH"

PAYMENTS_COLUMNS = [
    "payment_id",
    "user_id",
    "idempotency_key",
    "provider",
    "currency",
    "amount",
    "status",
    "created_at",
    "updated_at",
    "completed_at",
]

PAYMENT_EVENTS_COLUMNS = [
    "event_id",
    "payment_id",
    "event_type",
    "old_status",
    "new_status",
    "event_time",
    "source",
]

PROVIDER_CALLBACKS_COLUMNS = [
    "callback_id",
    "payment_id",
    "provider",
    "provider_status",
    "tx_hash",
    "blockchain_network",
    "received_at",
]

LEDGER_COLUMNS = [
    "entry_id",
    "transaction_id",
    "payment_id",
    "user_id",
    "currency",
    "entry_type",
    "amount",
    "created_at",
]


def connect_to_clickhouse():
    return clickhouse_connect.get_client(
        host="localhost",
        port=8123,
        username="default",
        password="",
        database="qa_lab",
    )


def make_uuid() -> str:
    return str(uuid4())


def make_tx_hash() -> str:
    return "0x" + f"{random.getrandbits(128):032x}"


def money(value: str) -> Decimal:
    return Decimal(value)


def add_payment(
    payments: list[tuple],
    *,
    payment_id: str,
    user_id: int,
    idempotency_key: str,
    currency: str,
    amount: Decimal,
    status: str,
    created_at: datetime,
    updated_at: datetime,
    completed_at: datetime | None,
) -> None:
    payments.append(
        (
            payment_id,
            user_id,
            idempotency_key,
            PROVIDER,
            currency,
            amount,
            status,
            created_at,
            updated_at,
            completed_at,
        )
    )


def add_event(
    events: list[tuple],
    *,
    payment_id: str,
    old_status: str,
    new_status: str,
    event_time: datetime,
    source: str = "payment-service",
) -> None:
    events.append(
        (
            make_uuid(),
            payment_id,
            "status_changed",
            old_status,
            new_status,
            event_time,
            source,
        )
    )


def add_callback(
    callbacks: list[tuple],
    *,
    payment_id: str,
    provider_status: str,
    received_at: datetime,
    tx_hash: str | None = None,
) -> None:
    callbacks.append(
        (
            make_uuid(),
            payment_id,
            PROVIDER,
            provider_status,
            tx_hash,
            NETWORK,
            received_at,
        )
    )


def add_balanced_ledger(
    ledger_entries: list[tuple],
    *,
    payment_id: str,
    user_id: int,
    currency: str,
    amount: Decimal,
    created_at: datetime,
) -> None:
    transaction_id = make_uuid()

    ledger_entries.append(
        (
            make_uuid(),
            transaction_id,
            payment_id,
            user_id,
            currency,
            "debit",
            amount,
            created_at,
        )
    )

    ledger_entries.append(
        (
            make_uuid(),
            transaction_id,
            payment_id,
            user_id,
            currency,
            "credit",
            amount,
            created_at,
        )
    )


def add_imbalanced_ledger(
    ledger_entries: list[tuple],
    *,
    payment_id: str,
    user_id: int,
    currency: str,
    debit_amount: Decimal,
    credit_amount: Decimal,
    created_at: datetime,
) -> None:
    transaction_id = make_uuid()

    ledger_entries.append(
        (
            make_uuid(),
            transaction_id,
            payment_id,
            user_id,
            currency,
            "debit",
            debit_amount,
            created_at,
        )
    )

    ledger_entries.append(
        (
            make_uuid(),
            transaction_id,
            payment_id,
            user_id,
            currency,
            "credit",
            credit_amount,
            created_at,
        )
    )


def generate_seed_data():
    random.seed(42)

    now = datetime.now().replace(microsecond=0)

    payments = []
    events = []
    callbacks = []
    ledger_entries = []

    currencies = ["USDT", "BTC", "ETH", "USDC"]

    # Scenario 1: normal completed payments
    for i in range(20):
        payment_id = make_uuid()
        user_id = 1000 + i
        currency = random.choice(currencies)
        amount = money(str(random.choice(["25.00000000", "50.50000000", "125.75000000", "300.00000000"])))

        created_at = now - timedelta(minutes=120 - i)
        processing_at = created_at + timedelta(minutes=1)
        completed_at = created_at + timedelta(minutes=random.randint(2, 10))

        add_payment(
            payments,
            payment_id=payment_id,
            user_id=user_id,
            idempotency_key=f"idem-happy-{i:03d}",
            currency=currency,
            amount=amount,
            status="completed",
            created_at=created_at,
            updated_at=completed_at,
            completed_at=completed_at,
        )

        add_event(
            events,
            payment_id=payment_id,
            old_status="none",
            new_status="created",
            event_time=created_at,
        )
        add_event(
            events,
            payment_id=payment_id,
            old_status="created",
            new_status="processing",
            event_time=processing_at,
        )
        add_event(
            events,
            payment_id=payment_id,
            old_status="processing",
            new_status="completed",
            event_time=completed_at,
        )

        add_callback(
            callbacks,
            payment_id=payment_id,
            provider_status="confirmed",
            tx_hash=make_tx_hash(),
            received_at=completed_at,
        )

        add_balanced_ledger(
            ledger_entries,
            payment_id=payment_id,
            user_id=user_id,
            currency=currency,
            amount=amount,
            created_at=completed_at,
        )

    # Scenario 2: duplicate idempotency key
    duplicate_key = "idem-duplicate-001"

    for i in range(2):
        payment_id = make_uuid()
        user_id = 2001
        created_at = now - timedelta(minutes=30 - i)

        add_payment(
            payments,
            payment_id=payment_id,
            user_id=user_id,
            idempotency_key=duplicate_key,
            currency="USDT",
            amount=money("75.00000000"),
            status="completed",
            created_at=created_at,
            updated_at=created_at + timedelta(minutes=3),
            completed_at=created_at + timedelta(minutes=3),
        )

        add_event(
            events,
            payment_id=payment_id,
            old_status="none",
            new_status="created",
            event_time=created_at,
        )
        add_event(
            events,
            payment_id=payment_id,
            old_status="created",
            new_status="completed",
            event_time=created_at + timedelta(minutes=3),
        )

        add_callback(
            callbacks,
            payment_id=payment_id,
            provider_status="confirmed",
            tx_hash=make_tx_hash(),
            received_at=created_at + timedelta(minutes=3),
        )

        add_balanced_ledger(
            ledger_entries,
            payment_id=payment_id,
            user_id=user_id,
            currency="USDT",
            amount=money("75.00000000"),
            created_at=created_at + timedelta(minutes=3),
        )

    # Scenario 3: stuck payment
    stuck_payment_id = make_uuid()
    stuck_created_at = now - timedelta(minutes=60)

    add_payment(
        payments,
        payment_id=stuck_payment_id,
        user_id=3001,
        idempotency_key="idem-stuck-001",
        currency="BTC",
        amount=money("0.01500000"),
        status="processing",
        created_at=stuck_created_at,
        updated_at=now - timedelta(minutes=45),
        completed_at=None,
    )

    add_event(
        events,
        payment_id=stuck_payment_id,
        old_status="none",
        new_status="created",
        event_time=stuck_created_at,
    )
    add_event(
        events,
        payment_id=stuck_payment_id,
        old_status="created",
        new_status="processing",
        event_time=stuck_created_at + timedelta(minutes=1),
    )

    # Scenario 4: provider confirmed, internal payment is still processing
    mismatch_payment_id = make_uuid()
    mismatch_created_at = now - timedelta(minutes=40)

    add_payment(
        payments,
        payment_id=mismatch_payment_id,
        user_id=4001,
        idempotency_key="idem-provider-mismatch-001",
        currency="ETH",
        amount=money("0.25000000"),
        status="processing",
        created_at=mismatch_created_at,
        updated_at=mismatch_created_at + timedelta(minutes=2),
        completed_at=None,
    )

    add_event(
        events,
        payment_id=mismatch_payment_id,
        old_status="none",
        new_status="created",
        event_time=mismatch_created_at,
    )
    add_event(
        events,
        payment_id=mismatch_payment_id,
        old_status="created",
        new_status="processing",
        event_time=mismatch_created_at + timedelta(minutes=2),
    )

    add_callback(
        callbacks,
        payment_id=mismatch_payment_id,
        provider_status="confirmed",
        tx_hash=make_tx_hash(),
        received_at=mismatch_created_at + timedelta(minutes=4),
    )

    # Scenario 5: ledger imbalance
    imbalance_payment_id = make_uuid()
    imbalance_created_at = now - timedelta(minutes=25)
    imbalance_completed_at = imbalance_created_at + timedelta(minutes=5)

    add_payment(
        payments,
        payment_id=imbalance_payment_id,
        user_id=5001,
        idempotency_key="idem-ledger-imbalance-001",
        currency="USDT",
        amount=money("100.00000000"),
        status="completed",
        created_at=imbalance_created_at,
        updated_at=imbalance_completed_at,
        completed_at=imbalance_completed_at,
    )

    add_event(
        events,
        payment_id=imbalance_payment_id,
        old_status="none",
        new_status="created",
        event_time=imbalance_created_at,
    )
    add_event(
        events,
        payment_id=imbalance_payment_id,
        old_status="created",
        new_status="completed",
        event_time=imbalance_completed_at,
    )

    add_callback(
        callbacks,
        payment_id=imbalance_payment_id,
        provider_status="confirmed",
        tx_hash=make_tx_hash(),
        received_at=imbalance_completed_at,
    )

    add_imbalanced_ledger(
        ledger_entries,
        payment_id=imbalance_payment_id,
        user_id=5001,
        currency="USDT",
        debit_amount=money("100.00000000"),
        credit_amount=money("99.00000000"),
        created_at=imbalance_completed_at,
    )

    # Scenario 6: invalid status transition: failed -> completed
    invalid_transition_payment_id = make_uuid()
    invalid_created_at = now - timedelta(minutes=20)

    add_payment(
        payments,
        payment_id=invalid_transition_payment_id,
        user_id=6001,
        idempotency_key="idem-invalid-transition-001",
        currency="USDC",
        amount=money("44.00000000"),
        status="completed",
        created_at=invalid_created_at,
        updated_at=invalid_created_at + timedelta(minutes=6),
        completed_at=invalid_created_at + timedelta(minutes=6),
    )

    add_event(
        events,
        payment_id=invalid_transition_payment_id,
        old_status="none",
        new_status="created",
        event_time=invalid_created_at,
    )
    add_event(
        events,
        payment_id=invalid_transition_payment_id,
        old_status="created",
        new_status="failed",
        event_time=invalid_created_at + timedelta(minutes=3),
    )
    add_event(
        events,
        payment_id=invalid_transition_payment_id,
        old_status="failed",
        new_status="completed",
        event_time=invalid_created_at + timedelta(minutes=6),
    )

    add_callback(
        callbacks,
        payment_id=invalid_transition_payment_id,
        provider_status="confirmed",
        tx_hash=make_tx_hash(),
        received_at=invalid_created_at + timedelta(minutes=6),
    )

    add_balanced_ledger(
        ledger_entries,
        payment_id=invalid_transition_payment_id,
        user_id=6001,
        currency="USDC",
        amount=money("44.00000000"),
        created_at=invalid_created_at + timedelta(minutes=6),
    )

    # Scenario 7: duplicate provider callbacks
    duplicate_callback_payment_id = make_uuid()
    duplicate_callback_created_at = now - timedelta(minutes=15)
    duplicate_callback_completed_at = duplicate_callback_created_at + timedelta(minutes=4)
    duplicate_tx_hash = make_tx_hash()

    add_payment(
        payments,
        payment_id=duplicate_callback_payment_id,
        user_id=7001,
        idempotency_key="idem-duplicate-callback-001",
        currency="USDT",
        amount=money("150.00000000"),
        status="completed",
        created_at=duplicate_callback_created_at,
        updated_at=duplicate_callback_completed_at,
        completed_at=duplicate_callback_completed_at,
    )

    add_event(
        events,
        payment_id=duplicate_callback_payment_id,
        old_status="none",
        new_status="created",
        event_time=duplicate_callback_created_at,
    )
    add_event(
        events,
        payment_id=duplicate_callback_payment_id,
        old_status="created",
        new_status="completed",
        event_time=duplicate_callback_completed_at,
    )

    add_callback(
        callbacks,
        payment_id=duplicate_callback_payment_id,
        provider_status="confirmed",
        tx_hash=duplicate_tx_hash,
        received_at=duplicate_callback_completed_at,
    )
    add_callback(
        callbacks,
        payment_id=duplicate_callback_payment_id,
        provider_status="confirmed",
        tx_hash=duplicate_tx_hash,
        received_at=duplicate_callback_completed_at + timedelta(seconds=10),
    )

    add_balanced_ledger(
        ledger_entries,
        payment_id=duplicate_callback_payment_id,
        user_id=7001,
        currency="USDT",
        amount=money("150.00000000"),
        created_at=duplicate_callback_completed_at,
    )

    return payments, events, callbacks, ledger_entries


def truncate_tables(client) -> None:
    tables = [
        "payments",
        "payment_events",
        "provider_callbacks",
        "ledger_entries",
    ]

    for table in tables:
        client.command(f"TRUNCATE TABLE qa_lab.{table}")


def save_seed_summary(
    payments: list[tuple],
    events: list[tuple],
    callbacks: list[tuple],
    ledger_entries: list[tuple],
) -> None:
    output_dir = Path("data/generated")
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "payments": len(payments),
        "payment_events": len(events),
        "provider_callbacks": len(callbacks),
        "ledger_entries": len(ledger_entries),
        "included_problem_scenarios": [
            "duplicate idempotency key",
            "stuck payment",
            "provider/internal status mismatch",
            "ledger imbalance",
            "invalid status transition",
            "duplicate provider callbacks",
        ],
    }

    summary_file = output_dir / "seed_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main() -> None:
    client = connect_to_clickhouse()

    payments, events, callbacks, ledger_entries = generate_seed_data()

    truncate_tables(client)

    client.insert(
        "payments",
        payments,
        column_names=PAYMENTS_COLUMNS,
    )

    client.insert(
        "payment_events",
        events,
        column_names=PAYMENT_EVENTS_COLUMNS,
    )

    client.insert(
        "provider_callbacks",
        callbacks,
        column_names=PROVIDER_CALLBACKS_COLUMNS,
    )

    client.insert(
        "ledger_entries",
        ledger_entries,
        column_names=LEDGER_COLUMNS,
    )

    save_seed_summary(payments, events, callbacks, ledger_entries)

    print("Seed data loaded successfully.")
    print(f"payments: {len(payments)}")
    print(f"payment_events: {len(events)}")
    print(f"provider_callbacks: {len(callbacks)}")
    print(f"ledger_entries: {len(ledger_entries)}")
    print("Summary saved to data/generated/seed_summary.json")


if __name__ == "__main__":
    main()