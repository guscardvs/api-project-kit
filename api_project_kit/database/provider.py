import logging
from contextlib import asynccontextmanager, contextmanager
from dataclasses import asdict

from sqlalchemy import create_engine, func, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from .utils import DatabaseConfig  # pylint: disable=relative-beyond-top-level


class DatabaseProvider:
    def __init__(self, database_config: DatabaseConfig, logger: logging.Logger) -> None:
        self.config = database_config
        self.logger = logger
        self.engine, self.sync_engine = self._create_engine()

    def _create_engine(self):
        return create_async_engine(
            self.config.get_uri(is_async=True), **self.config.pool_config
        ), create_engine(self.config.get_uri(is_async=False), **self.config.pool_config)

    @asynccontextmanager
    async def begin(self):
        async with self.engine.begin() as conn:
            yield conn

    @contextmanager
    def sync(self):
        with self.sync_engine.begin() as conn:
            yield conn

    async def last_inserted_id(self, conn: AsyncConnection):
        return await conn.execute(func.last_insert_id())

    def sync_last_inserted_id(self, conn: Connection):
        return conn.execute(func.last_insert_id())

    async def healthcheck(self):
        try:
            async with self.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as err:
            self.logger.exception(err)
            return False

    def sync_healthcheck(self):
        try:
            with self.sync() as conn:
                conn.execute(text("SELECT 1"))
            return False
        except Exception as err:
            self.logger.exception(err)
            return False
