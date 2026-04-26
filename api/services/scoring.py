from tortoise.transactions import in_transaction

from api.core.exceptions import TransactionNotFoundError
from api.core.model_loader import get_model, get_threshold
from api.domain.fraud_scoring import score_request
from api.repositories import transactions as transaction_repo
from api.schemas import ScoreRequest, ScoreResponse, TransactionUpdate


def score_payload(
    payload: ScoreRequest,
    *,
    model=None,
    threshold: float | None = None,
) -> tuple[float, int, float]:
    scoring_model = model or get_model()
    scoring_threshold = threshold if threshold is not None else get_threshold()
    fraud_probability, decision = score_request(
        payload, model=scoring_model, threshold=scoring_threshold
    )
    return fraud_probability, decision, scoring_threshold


async def create_or_score_transaction(payload: ScoreRequest) -> ScoreResponse:
    fraud_probability, decision, threshold = score_payload(payload)
    payload_data = payload.model_dump()
    create_defaults = payload_data.copy()
    create_defaults.pop("transaction_id", None)

    async with in_transaction() as connection:
        transaction, _ = await transaction_repo.get_or_create_transaction(
            transaction_id=payload.transaction_id,
            defaults=create_defaults,
            connection=connection,
        )

        prediction = await transaction_repo.create_prediction(
            transaction=transaction,
            fraud_probability=fraud_probability,
            decision=decision,
            connection=connection,
        )

    return ScoreResponse(
        transaction_id=payload.transaction_id,
        fraud_probability=fraud_probability,
        decision=decision,
        threshold=threshold,
        scored_at=prediction.scored_at,
    )


async def update_and_rescore_transaction(
    transaction_id: str,
    payload: TransactionUpdate,
) -> ScoreResponse:
    update_data = payload.model_dump(exclude_none=True)

    async with in_transaction() as connection:
        tx = await transaction_repo.get_transaction_for_update(
            transaction_id,
            connection=connection,
        )
        if tx is None:
            raise TransactionNotFoundError(transaction_id)

        score_payload_data = ScoreRequest(
            transaction_id=transaction_id,
            amount=update_data.get("amount", tx.amount),
            transaction_hour=update_data.get("transaction_hour", tx.transaction_hour),
            merchant_category=update_data.get(
                "merchant_category", tx.merchant_category
            ),
            foreign_transaction=update_data.get(
                "foreign_transaction", tx.foreign_transaction
            ),
            location_mismatch=update_data.get(
                "location_mismatch", tx.location_mismatch
            ),
            device_trust_score=update_data.get(
                "device_trust_score", tx.device_trust_score
            ),
            velocity_last_24h=update_data.get(
                "velocity_last_24h", tx.velocity_last_24h
            ),
            cardholder_age=update_data.get("cardholder_age", tx.cardholder_age),
        )
        fraud_probability, decision, threshold = score_payload(score_payload_data)

        await transaction_repo.update_transaction_fields(
            tx,
            fields=update_data,
            connection=connection,
        )

        prediction = await transaction_repo.create_prediction(
            transaction=tx,
            fraud_probability=fraud_probability,
            decision=decision,
            connection=connection,
        )

    return ScoreResponse(
        transaction_id=transaction_id,
        fraud_probability=fraud_probability,
        decision=decision,
        threshold=threshold,
        scored_at=prediction.scored_at,
    )
