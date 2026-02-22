from collections.abc import Generator

from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.logfire import get_logger

Base = declarative_base()
logger = get_logger(__name__)


def init_engine(
    database_uri: str, *, echo: bool = False
) -> tuple[Engine, sessionmaker]:
    logger.debug("Initializing SQLAlchemy engine")
    engine = create_engine(
        database_uri,
        echo=echo,
        pool_pre_ping=True,
    )
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    return engine, SessionLocal


def create_db_and_tables(engine: Engine) -> None:
    logger.debug("Creating database tables")
    Base.metadata.create_all(bind=engine)


def drop_db_and_tables(engine: Engine) -> None:
    logger.debug("Dropping database tables")
    Base.metadata.drop_all(bind=engine)


def get_session(request: Request) -> Generator[Session, None, None]:
    SessionLocal = request.app.state.SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
