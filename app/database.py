from typing import Generator

from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

Base = declarative_base()


def init_engine(
    database_uri: str, *, echo: bool = False
) -> tuple[Engine, sessionmaker]:
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
    Base.metadata.create_all(bind=engine)


def drop_db_and_tables(engine: Engine) -> None:
    Base.metadata.drop_all(bind=engine)


def get_session(request: Request) -> Generator[Session, None, None]:
    SessionLocal = request.app.state.SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
