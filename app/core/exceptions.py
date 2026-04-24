from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code = 500
    detail = "Internal server error"

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.detail
        super().__init__(self.detail)


class BadRequestError(AppError):
    status_code = 400
    detail = "Bad request"


class NotFoundError(AppError):
    status_code = 404
    detail = "Not found"


class TransactionNotFoundError(NotFoundError):
    def __init__(self, transaction_id: str) -> None:
        super().__init__(f"Transaction not found: {transaction_id}")


class InvalidUploadError(BadRequestError):
    pass


class InvalidCSVError(BadRequestError):
    pass


class CreateOrScoreFailedError(AppError):
    def __init__(self, transaction_id: str) -> None:
        super().__init__(f"Create-and-score failed for transaction: {transaction_id}")


class UpdateOrRescoreFailedError(AppError):
    def __init__(self, transaction_id: str) -> None:
        super().__init__(f"Update-and-rescore failed for transaction: {transaction_id}")


class CSVImportFailedError(AppError):
    def __init__(self, filename: str | None) -> None:
        file_label = filename or "<unknown>"
        super().__init__(f"CSV import failed for file: {file_label}")


async def app_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, AppError):
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
