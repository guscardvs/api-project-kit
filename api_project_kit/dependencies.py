from fastapi import Depends, Request

from .database import DatabaseProvider
from .http import HttpProvider


def _get_database_provider(request: Request) -> DatabaseProvider:
    return request.app.state.database_provider


def DatabaseDepends():
    return Depends(_get_database_provider)


def _get_http_provider(request: Request) -> HttpProvider:
    return request.app.state.http_provider


def HttpDepends():

    return Depends(_get_http_provider)
