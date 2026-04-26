import asyncio
from pathlib import Path

from api.config import settings
from api.core.logfire import configure_logfire, get_logger
from api.database import close_db, init_db
from api.services.csv_import import import_transactions_from_csv

REPO_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = REPO_ROOT / "resources" / "credit_card_fraud_10k.csv"
logger = get_logger(__name__)


async def import_transactions_from_path(csv_path: Path = CSV_PATH) -> None:
    if not csv_path.exists():
        msg = f"CSV file not found: {csv_path}"
        raise FileNotFoundError(msg)

    await init_db(settings.DATABASE_URI, generate_schemas=True)
    try:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            summary = await import_transactions_from_csv(csv_stream=csv_file)
        logger.info(
            "Initial migration import complete: total=%s imported=%s duplicates=%s invalid=%s scoring_errors=%s",
            summary.total_rows,
            summary.imported,
            summary.skipped_duplicates,
            summary.skipped_invalid,
            summary.skipped_scoring_errors,
        )
    finally:
        await close_db()


if __name__ == "__main__":
    configure_logfire(settings)
    asyncio.run(import_transactions_from_path())
