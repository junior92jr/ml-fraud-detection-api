import csv

from pydantic import ValidationError
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.core.logfire import configure_logfire, get_logger
from app.database import init_engine
from app.models import Transaction
from app.schemas import MerchantCategory, TransactionCreate

CSV_PATH = "resources/credit_card_fraud_10k.csv"
MERCHANT_CATEGORIES: dict[str, MerchantCategory] = {
    "Electronics": "Electronics",
    "Travel": "Travel",
    "Grocery": "Grocery",
    "Food": "Food",
    "Clothing": "Clothing",
}


def parse_bool(value: str) -> bool:
    return bool(int(value))


def import_transactions(session_factory: sessionmaker) -> None:
    logger = get_logger("import_transactions")
    inserted = 0
    skipped_duplicates = 0

    session: Session = session_factory()

    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                merchant_category = MERCHANT_CATEGORIES[row["merchant_category"]]

                data = TransactionCreate(
                    transaction_id=row["transaction_id"],
                    amount=float(row["amount"]),
                    transaction_hour=int(row["transaction_hour"]),
                    merchant_category=merchant_category,
                    foreign_transaction=parse_bool(row["foreign_transaction"]),
                    location_mismatch=parse_bool(row["location_mismatch"]),
                    device_trust_score=int(row["device_trust_score"]),
                    velocity_last_24h=int(row["velocity_last_24h"]),
                    cardholder_age=int(row["cardholder_age"]),
                )
            except (ValueError, KeyError, ValidationError):
                logger.exception(
                    "Skipping invalid row %s", row.get("transaction_id", "N/A")
                )
                continue

            existing = (
                session.query(Transaction)
                .filter_by(transaction_id=data.transaction_id)
                .first()
            )
            if existing:
                logger.warning(
                    f"Skipping duplicate transaction_id {data.transaction_id}"
                )
                skipped_duplicates += 1
                continue

            session.add(Transaction(**data.model_dump()))
            inserted += 1

    session.commit()
    session.close()

    logger.info(
        f"Imported {inserted} transactions, skipped {skipped_duplicates} duplicates"
    )


if __name__ == "__main__":
    configure_logfire(settings)
    engine, SessionLocal = init_engine(settings.DATABASE_URI, echo=True)

    import_transactions(SessionLocal)
