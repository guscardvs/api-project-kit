import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from urllib.parse import urlparse

from aiohttp import ClientSession, ContentTypeError

from api_project_kit import exc


class HttpProvider:
    def __init__(self, logger: logging.Logger):
        self.loaded = False
        self.logger = logger
        self.init()

    def init(self):
        if self.loaded:
            return
        self.logger.info("Starting HTTP Session Manager")
        self.clients: dict[str, ClientSession] = {}
        self._get_client("http://default")
        self.loaded = True

    async def finish(self):
        self.logger.info("Stopping HTTP Session Manager")
        await asyncio.gather(*[value.close() for value in self.clients.values()])
        self.loaded = False

    def _get_client(self, url: str):
        name = urlparse(url).netloc
        if client := self.clients.get(name):
            return client
        self.clients[name] = ClientSession()
        return self.clients[name]

    def get_client(self, url: str):
        return self._get_client(url)

    @asynccontextmanager
    async def request(
        self, method: str, url: str, **kwargs
    ) -> AsyncGenerator[tuple[dict[str, Any], int], None]:
        async with self.get_client(url).request(method, url, **kwargs) as response:
            try:
                yield (await response.json(encoding="utf8"), response.status)
            except ContentTypeError:
                raise

    def get(self, url: str, *, params: dict[str, Any] = None, **kwargs):
        return self.request("GET", url, params=params or {}, **kwargs)

    def post(
        self,
        url: str,
        *,
        json: dict[str, Any] = None,
        data: dict[str, Any] = None,
        **kwargs,
    ):
        if json:
            return self.request("POST", url, json=json or {}, **kwargs)
        return self.request("POST", url, data=data or {}, **kwargs)
