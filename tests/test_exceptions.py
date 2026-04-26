import pytest
from starlette.requests import Request

from api.core.exceptions import CSVImportFailedError, app_error_handler


@pytest.mark.anyio
async def test_app_error_handler_returns_generic_500_for_unexpected_exception():
    request = Request(scope={"type": "http", "method": "GET", "path": "/"})

    response = await app_error_handler(request, RuntimeError("boom"))

    assert response.status_code == 500
    assert response.body == b'{"detail":"Internal server error"}'


def test_csv_import_failed_error_handles_missing_filename():
    error = CSVImportFailedError(None)
    assert error.detail == "CSV import failed for file: <unknown>"
