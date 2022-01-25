from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


class EnvironmentNotSet(Exception):
    def __init__(self, key: str) -> None:
        self.key = key

    def __str__(self) -> str:
        return 'The env key {self.key} is unset'


class ApiError(Exception):

    status_code = HTTP_400_BAD_REQUEST

    __msg: str

    def get_message(self) -> str:
        try:
            return self.__msg
        except AttributeError:
            return "An error occurred"

    def set_msg(self, msg: str):
        self.__msg = msg

    @classmethod
    def from_message(cls, message: str, status_code: int = None):
        exc = cls()
        exc.set_msg(message)
        exc.status_code = status_code or cls.status_code
        return exc


class RepositoryError(ApiError):
    def __init__(self, obj: str = "Object") -> None:
        self._object = obj
        super().__init__(obj)

    @classmethod
    def from_obj(cls, obj: str = "Object"):
        return cls(obj)


class DoesNotExist(RepositoryError):
    status_code = HTTP_404_NOT_FOUND

    def get_message(self) -> str:
        return '{self._object} not found'


class AlreadyExists(RepositoryError):
    def get_message(self) -> str:
        return '{self._object} already exists'


class UnexpectedError(ApiError):
    def __init__(self) -> None:
        pass

    status_code = HTTP_500_INTERNAL_SERVER_ERROR

    def get_message(self) -> str:
        return "An unexpected error occured, talk to the tech team"


class UnAuthorizedError(ApiError):
    def __init__(self) -> None:
        pass

    status_code = HTTP_403_FORBIDDEN

    def get_message(self) -> str:
        return "You do not have permission to use this route"


class InvalidOrExpiredToken(ApiError):
    def __init__(self) -> None:
        pass

    status_code = HTTP_401_UNAUTHORIZED

    def get_message(self) -> str:
        return "Token is invalid or expired"
