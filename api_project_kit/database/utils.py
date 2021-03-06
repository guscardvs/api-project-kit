import abc
import enum
from dataclasses import dataclass


class DriverTypes(abc.ABC):
    @property
    @abc.abstractmethod
    def port(self) -> int:
        """Returns default port for database"""

    @property
    @abc.abstractmethod
    def async_driver(self) -> str:
        """Returns sqlalchemy prepared str with async driver
        example: mysql+aiomysql
        """

    @property
    @abc.abstractmethod
    def sync_driver(self) -> str:
        """Returns sqlalchemy prepared str with synchronous driver
        example: mysql+pymysql
        """

    def get_connection_uri(self, is_async: bool, cfg: "DatabaseConfig") -> str:
        """Returns autogenerated driver uri for sqlalchemy create_engine()"""
        driver_prefix = self.async_driver if is_async else self.sync_driver
        return "{driver}://{user}:{passwd}@{host}:{port}/{name}".format(
            driver=driver_prefix,
            user=cfg.user,
            passwd=cfg.passwd,
            port=cfg.get_port(),
            name=cfg.name,
        )


class MysqlDriver(DriverTypes):
    """Driver Default values for MySQL Connection"""

    port = 3306
    async_driver = "mysql+aiomysql"
    sync_driver = "mysql+pymysql"


class PostgresDriver(DriverTypes):
    """Driver Default values for PostgreSQL Connection"""

    port = 5432
    async_driver = "postgresql+asyncpg"
    sync_driver = "postgresql+psycopg2"


class SqliteDriver(DriverTypes):
    """Driver Default values for Sqlite Connection"""

    port = 0
    async_driver = "sqlite+aiosqlite"
    sync_driver = "sqlite"

    def get_connection_uri(self, is_async: bool, cfg: "DatabaseConfig") -> str:
        """Returns autogenerated driver uri for sqlalchemy create_engine()"""
        driver_prefix = self.async_driver if is_async else self.sync_driver
        return "{driver}:///{name}".format(driver=driver_prefix, name=cfg.name)


@dataclass(frozen=True)
class DatabaseConfig:
    """Database configuration params
    Obs: pass filename as name if using sqlite"""

    driver: DriverTypes
    host: str
    name: str
    user: str = ""
    passwd: str = ""
    port: int = -1
    _pool_size: int = 20
    _pool_recycle: int = 3600
    _max_overflow: int = 0

    def get_port(self):
        return self.port if self.port != -1 else self.driver.port

    def get_uri(self, *, is_async: bool):
        return self.driver.get_connection_uri(is_async, self)

    @property
    def pool_config(self) -> dict[str, int]:
        if isinstance(self.driver, SqliteDriver):
            return {}
        return {
            "pool_size": self._pool_size,
            "pool_recycle": self._pool_recycle,
            "max_overflow": self._max_overflow,
        }
