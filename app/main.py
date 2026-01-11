from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import Settings, settings
from app.database import create_db_and_tables, init_engine
from app.routers import score, transactions
from app.utils.logger import logger_config

logger = logger_config(__name__)


def create_application(settings: Settings) -> FastAPI:
    engine, SessionLocal = init_engine(settings.DATABASE_URI, echo=True)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        create_db_and_tables(engine)

        app.state.engine = engine
        app.state.SessionLocal = SessionLocal

        logger.info("startup: DB initialized")
        yield
        logger.info("shutdown: triggered")

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        docs_url="/",
        lifespan=lifespan,
    )

    app.include_router(score.router, prefix="/score", tags=["Scoring"])
    app.include_router(
        transactions.router, prefix="/transactions", tags=["Transactions"]
    )

    return app


app = create_application(settings)
