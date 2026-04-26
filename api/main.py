from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from api.config import Settings, settings
from api.core.exceptions import register_exception_handlers
from api.core.logfire import configure_logfire, get_logger
from api.core.model_loader import get_model_bundle
from api.database import close_db, init_db
from api.routers import transactions

logger = get_logger(__name__)


def create_application(settings: Settings) -> FastAPI:
    configure_logfire(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        configure_logfire(settings, app=app)
        get_model_bundle()
        logger.info("startup: model bundle loaded")
        await init_db(
            settings.DATABASE_URI,
            generate_schemas=settings.DB_GENERATE_SCHEMAS,
        )

        logger.info("startup: DB initialized")
        yield
        await close_db()
        logger.info("shutdown: triggered")

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        docs_url=None,
        redoc_url=None,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)

    @app.get("/", include_in_schema=False)
    async def scalar_docs():
        return get_scalar_api_reference(
            openapi_url=app.openapi_url,
            title=f"{settings.PROJECT_NAME} - Scalar API",
        )

    app.include_router(
        transactions.router, prefix="/transactions", tags=["Transactions"]
    )

    return app


app = create_application(settings)
