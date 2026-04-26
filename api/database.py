from tortoise import Tortoise

from api.core.logfire import get_logger

logger = get_logger(__name__)


async def init_db(database_uri: str, *, generate_schemas: bool = True) -> None:
    logger.debug("Initializing Tortoise ORM")
    await Tortoise.init(
        db_url=database_uri,
        modules={"models": ["api.models"]},
    )
    if generate_schemas:
        await Tortoise.generate_schemas()


async def close_db() -> None:
    logger.debug("Closing database connections")
    await Tortoise.close_connections()


async def reset_tables() -> None:
    logger.debug("Resetting database tables")
    from api.models import Prediction, Transaction

    await Prediction.all().delete()
    await Transaction.all().delete()
