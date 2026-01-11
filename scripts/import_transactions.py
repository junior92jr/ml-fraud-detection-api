import csv

from sqlalchemy.orm import Session, sessionmaker

from app.database import init_engine
from app.models import Transaction
from app.schemas import TransactionCreate
from app.utils.logger import logger_config

CSV_PATH = "resources/credit_card_fraud_10k.csv"


def parse_bool(value: str) -> bool:
    return bool(int(value))


def import_transactions(session_factory: sessionmaker) -> None:
    logger = logger_config("import_transactions")
    inserted = 0
    skipped_duplicates = 0

    session: Session = session_factory()

    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                data = TransactionCreate(
                    transaction_id=row["transaction_id"],
                    amount=float(row["amount"]),
                    transaction_hour=int(row["transaction_hour"]),
                    merchant_category=row["merchant_category"],
                    foreign_transaction=parse_bool(row["foreign_transaction"]),
                    location_mismatch=parse_bool(row["location_mismatch"]),
                    device_trust_score=int(row["device_trust_score"]),
                    velocity_last_24h=int(row["velocity_last_24h"]),
                    cardholder_age=int(row["cardholder_age"]),
                )
            except Exception as e:
                logger.error(
                    f"Skipping invalid row {row.get('transaction_id', 'N/A')}: {e}"
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
    from app.config import settings
    from app.database import init_engine

    engine, SessionLocal = init_engine(settings.DATABASE_URI, echo=True)

    import_transactions(SessionLocal)
