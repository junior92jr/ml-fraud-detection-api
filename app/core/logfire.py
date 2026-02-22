from __future__ import annotations

import logging
from typing import Any

import logfire
from fastapi import FastAPI
from sqlalchemy.engine import Engine

from app.config import Settings

_is_configured = False
_is_logging_configured = False


def _parse_level(level_name: str) -> int:
    level = getattr(logging, level_name.upper(), None)
    if isinstance(level, int):
        return level
    return logging.WARNING


def _render_message(message: str, args: tuple[Any, ...]) -> str:
    if not args:
        return message
    try:
        return message % args
    except TypeError:
        return f"{message} {' '.join(str(arg) for arg in args)}"


def _configure_stdlib_logging() -> None:
    global _is_logging_configured
    if _is_logging_configured:
        return
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    _is_logging_configured = True


def configure_logfire(
    settings: Settings,
    *,
    app: FastAPI | None = None,
    engine: Engine | None = None,
) -> None:
    global _is_configured
    _configure_stdlib_logging()
    logging.getLogger().setLevel(_parse_level(settings.LOG_LEVEL))

    if not _is_configured:
        logfire.configure(
            send_to_logfire="if-token-present",
            token=settings.LOGFIRE_TOKEN or None,
            service_name=settings.LOGFIRE_SERVICE_NAME,
            service_version=settings.VERSION,
            environment=settings.LOGFIRE_ENVIRONMENT,
        )
        _is_configured = True

    if app is not None:
        try:
            logfire.instrument_fastapi(app)
        except RuntimeError as exc:
            logging.getLogger(__name__).warning(
                "FastAPI instrumentation unavailable: %s", exc
            )
    if engine is not None:
        try:
            logfire.instrument_sqlalchemy(engine=engine)
        except RuntimeError as exc:
            logging.getLogger(__name__).warning(
                "SQLAlchemy instrumentation unavailable: %s", exc
            )


class LogfireLogger:
    def __init__(self, name: str) -> None:
        self.name = name

    def debug(self, message: str, *args: Any) -> None:
        rendered = _render_message(message, args)
        logfire.debug("{name}: {message}", name=self.name, message=rendered)

    def info(self, message: str, *args: Any) -> None:
        rendered = _render_message(message, args)
        logfire.info("{name}: {message}", name=self.name, message=rendered)

    def warning(self, message: str, *args: Any) -> None:
        rendered = _render_message(message, args)
        logfire.warning("{name}: {message}", name=self.name, message=rendered)

    def error(self, message: str, *args: Any) -> None:
        rendered = _render_message(message, args)
        logfire.error("{name}: {message}", name=self.name, message=rendered)

    def exception(self, message: str, *args: Any) -> None:
        rendered = _render_message(message, args)
        logfire.exception("{name}: {message}", name=self.name, message=rendered)


def get_logger(name: str) -> LogfireLogger:
    return LogfireLogger(name)
