import logging

from fastapi import APIRouter, FastAPI

from .database import DatabaseConfig, DatabaseProvider
from .exc import set_api_error_handler
from .http import HttpProvider


def create_startup_handler(
    _app: FastAPI, database_config: DatabaseConfig, logger: logging.Logger
):
    def _startup():
        _app.state.database_provider = DatabaseProvider(database_config, logger)
        _app.state.http_provider = HttpProvider(logger)

    return _startup


def create_shutdown_handler(_app: FastAPI):
    async def _shutdown():
        await _app.state.http_provider.finish()

    return _shutdown


def get_application(
    *,
    title: str,
    prefix: str = "",
    logger: logging.Logger,
    router: APIRouter,
    database_config: DatabaseConfig,
):
    _app = FastAPI(
        title=title,
        openapi_url=f"{prefix}/openapi.json",
        docs_url=f"{prefix}/docs",
        redoc_url=f"{prefix}/redoc",
    )
    _app.include_router(router, prefix=f"{prefix}")

    _app.add_event_handler(
        "startup", create_startup_handler(_app, database_config, logger)
    )
    _app.add_event_handler("shutdown", create_shutdown_handler(_app))
    set_api_error_handler(_app)

    return _app
