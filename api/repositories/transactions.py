from datetime import UTC, datetime
from typing import Any, TypedDict

from app.models import Prediction, Transaction


class PredictionRow(TypedDict):
    id: int
    transaction_id: str
    fraud_probability: float
    decision: int
    scored_at: datetime


async def list_transactions(*, limit: int, offset: int) -> list[Transaction]:
    return await Transaction.all().order_by("-created_at").offset(offset).limit(limit)


async def count_transactions() -> int:
    return await Transaction.all().count()


async def list_scores(*, limit: int, offset: int) -> list[PredictionRow]:
    rows = (
        await Prediction.all()
        .order_by("-scored_at")
        .offset(offset)
        .limit(limit)
        .values("id", "transaction__transaction_id", "fraud_probability", "decision", "scored_at")
    )
    return [
        PredictionRow(
            id=row["id"],
            transaction_id=row["transaction__transaction_id"],
            fraud_probability=row["fraud_probability"],
            decision=row["decision"],
            scored_at=row["scored_at"],
        )
        for row in rows
    ]


async def count_scores() -> int:
    return await Prediction.all().count()


async def get_transaction_by_external_id(transaction_id: str) -> Transaction | None:
    return await Transaction.get_or_none(transaction_id=transaction_id)


async def list_prediction_rows_for_transaction(
    transaction: Transaction,
) -> list[PredictionRow]:
    rows = await (
        Prediction.filter(transaction=transaction)
        .order_by("-scored_at")
        .values("id", "fraud_probability", "decision", "scored_at")
    )
    return [
        PredictionRow(
            id=row["id"],
            transaction_id=transaction.transaction_id,
            fraud_probability=row["fraud_probability"],
            decision=row["decision"],
            scored_at=row["scored_at"],
        )
        for row in rows
    ]


async def get_or_create_transaction(
    *,
    transaction_id: str,
    defaults: dict[str, Any],
    connection: Any,
) -> tuple[Transaction, bool]:
    return await Transaction.get_or_create(
        transaction_id=transaction_id,
        defaults=defaults,
        using_db=connection,
    )


async def get_transaction_for_update(
    transaction_id: str,
    *,
    connection: Any,
) -> Transaction | None:
    return await (
        Transaction.filter(transaction_id=transaction_id)
        .using_db(connection)
        .select_for_update()
        .get_or_none()
    )


async def update_transaction_fields(
    transaction: Transaction,
    *,
    fields: dict[str, Any],
    connection: Any,
) -> None:
    for field_name, value in fields.items():
        setattr(transaction, field_name, value)
    await transaction.save(using_db=connection)


async def create_transaction(payload: dict[str, Any]) -> Transaction:
    return await Transaction.create(**payload)


async def create_prediction(
    *,
    transaction: Transaction,
    fraud_probability: float,
    decision: int,
    scored_at: datetime | None = None,
    connection: Any | None = None,
) -> Prediction:
    return await Prediction.create(
        transaction=transaction,
        fraud_probability=fraud_probability,
        decision=decision,
        scored_at=scored_at or datetime.now(UTC),
        using_db=connection,
    )
