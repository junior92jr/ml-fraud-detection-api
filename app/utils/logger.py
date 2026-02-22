from app.core.logfire import LogfireLogger, get_logger


def logger_config(module: str) -> LogfireLogger:
    return get_logger(module)
