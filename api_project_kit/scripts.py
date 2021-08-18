import pathlib
import subprocess
import typing

from typing_extensions import ParamSpec

T = typing.TypeVar("T")
P = ParamSpec("P")

import logging

from colorlog import ColoredFormatter

BASE_DIR = pathlib.Path(__file__).resolve().parent

# setting up colored log
def setup_log():
    logger = logging.getLogger("scripts.logger")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(
        ColoredFormatter(
            "%(log_color)s%(asctime)s - %(levelname)s: %(fg_white)s%(message)s (%(filename)s)",
            "%Y-%m-%d %H:%M:%S",
        )
    )

    logger.addHandler(handler)
    return logger


logger = setup_log()

# print_return automatically prints function return
def print_return(func: typing.Callable[P, T]) -> typing.Callable[P, T]:
    def inner(*args: P.args, **kwargs: P.kwargs):
        logger.info((response := func(*args, **kwargs)))
        return response

    return inner


# log exception instead of raising it with message
def say_if_failed(
    *, message: str, exc: type[Exception] = subprocess.CalledProcessError
):
    def outer(func: typing.Callable[P, T]) -> typing.Callable[P, typing.Optional[T]]:
        def inner(*args: P.args, **kwargs: P.kwargs):
            try:
                return func(*args, **kwargs)
            except exc:
                logger.error(message)

        return inner

    return outer


# run isort on all project files
@say_if_failed(message="Could not find isort")
@print_return
def isort():
    subprocess.run(["isort", str(BASE_DIR.parent)], capture_output=True, check=True)
    return "Imports sorted with isort"


# run black on all project files
@say_if_failed(message="Could not find black")
@print_return
def black():
    subprocess.run(["black", str(BASE_DIR.parent)], capture_output=True, check=True)
    return "Code restyled with black"


def fix():
    isort()
    black()


# add all files and then commit with commitizen
@say_if_failed(message="Something happened during your commit")
@print_return
def commit():
    fix()
    subprocess.run(["git", "add", str(BASE_DIR.parent)], check=True)
    subprocess.run(["cz", "c"], check=True)
    return "Finished commiting process"
