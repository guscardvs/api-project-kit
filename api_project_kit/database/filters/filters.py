import operator
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional, Union

from sqlalchemy import Column, Table, and_, false, or_, true
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.sql.elements import BooleanClauseList

from api_project_kit.database.filters import comparison


class Filter:
    def where(self, table: Table):
        pass

    @abstractmethod
    def __bool__(self):
        ...


@dataclass
class FieldFilter(Filter):
    field: str
    value: Optional[Any]
    comp: comparison.Comparison = comparison.Equal()
    enum_value: bool = False
    sql_func: Optional[Callable[[Column], Any]] = None

    def __eq__(self, filter: Filter) -> bool:
        if not isinstance(filter, type(self)):
            return False
        return (self.field, self.value, self.comp) == (
            filter.field,
            filter.value,
            filter.comp,
        )

    def __post_init__(self):
        if isinstance(self.value, bool) and not isinstance(self.comp, comparison.Null):
            self.value = true() if self.value else false()
        if isinstance(self.value, Enum):
            if self.enum_value:
                self.value = self.value and self.value.value
            else:
                self.value = self.value and self.value.name

    def where(self, table: Table):
        return self.attr(table)  # type: ignore

    def attr(self, table: Table):
        attr = self._attr(table, self.field)
        if not self:
            return True
        if self.sql_func:
            attr = self.sql_func(attr)  # type: ignore
        return self.comp.compare(attr, self.value)

    @staticmethod
    def _attr(table: Table, field: str) -> Union[Column, RelationshipProperty]:
        result = getattr(table.c, field, None)
        if result is None:
            raise NotImplementedError
        return result

    def __bool__(self):
        return self.value is not None


@dataclass(init=False)
class FilterJoins(Filter):
    operator: type[BooleanClauseList]
    filters: tuple[Filter, ...]

    def __init__(self, *filters: Filter) -> None:
        self.filters = filters

    def where(self, table: Table):
        return self.operator(*(f.where(table) for f in self.filters))

    def __bool__(self):
        return True


class OrFilter(FilterJoins):
    @property
    def operator(self):
        return or_


class AndFilter(FilterJoins):
    @property
    def operator(self):
        return and_
