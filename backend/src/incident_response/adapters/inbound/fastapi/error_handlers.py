import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from incident_response.domain.exceptions import (
    AdapterError,
    ConcurrencyError,
    DomainError,
    NotFoundError,
    ValidationError,
)

logger = logging.getLogger(__name__)


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    logger.warning("validation_error", extra={"field": exc.field, "message": exc.message})
    return JSONResponse(
        status_code=400,
        content={"code": exc.code, "message": exc.message, "field": exc.field},
    )


async def not_found_error_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"code": exc.code, "message": exc.message},
    )


async def concurrency_error_handler(request: Request, exc: ConcurrencyError) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"code": exc.code, "message": exc.message},
    )


async def adapter_error_handler(request: Request, exc: AdapterError) -> JSONResponse:
    logger.error(
        "adapter_error",
        extra={"adapter": exc.adapter, "message": exc.message},
        exc_info=exc.cause,
    )
    return JSONResponse(
        status_code=502,
        content={"code": exc.code, "message": f"External service error: {exc.adapter}"},
    )


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    logger.error("domain_error", extra={"code": exc.code, "message": exc.message})
    return JSONResponse(
        status_code=500,
        content={"code": exc.code, "message": exc.message},
    )


def register_error_handlers(app: FastAPI) -> None:
    """Register all domain error handlers with the FastAPI app."""
    app.add_exception_handler(ValidationError, validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(NotFoundError, not_found_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ConcurrencyError, concurrency_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(AdapterError, adapter_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(DomainError, domain_error_handler)  # type: ignore[arg-type]
