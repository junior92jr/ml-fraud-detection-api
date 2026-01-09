import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import score, transactions
from app.utils.logger import logger_config

logger = logger_config(__name__)

MODEL_PATH = os.getenv("MODEL_PATH", "/workspace/artifacts/model.joblib")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Triggers event before Fast API is started."""

    create_db_and_tables()

    logger.info("startup: triggered")
    logger.info("startup: DB initialized (model will be loaded lazily)")
    yield

    logger.info("shutdown: triggered")


def create_application() -> FastAPI:
    """Return a FastApi application."""

    application = FastAPI(
        docs_url="/",
        lifespan=lifespan,
    )

    application.include_router(score.router, prefix="/score", tags=["Scoring"])
    application.include_router(
        transactions.router, prefix="/transactions", tags=["Transactions"]
    )

    return application


app = create_application()
