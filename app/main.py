import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.inference.predictor import Predictor
from app.routers import predict, score, transactions
from app.utils.logger import logger_config

logger = logger_config(__name__)

MODEL_PATH = os.getenv("MODEL_PATH", "artifacts/model.joblib")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Triggers event before Fast API is started."""

    create_db_and_tables()

    logger.info("startup: triggered")

    # ML model init
    predictor = Predictor(MODEL_PATH)
    predictor.load()

    # Store predictor on app state
    app.state.predictor = predictor

    logger.info("startup: DB initialized, ML model loaded")

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

    application.include_router(
        predict.router,
        tags=["Prediction"],
    )

    return application


app = create_application()
