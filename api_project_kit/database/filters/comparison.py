import abc
from typing import Any, Union

from sqlalchemy import Boolean, Column
from sqlalchemy.sql.elements import BooleanClauseList
from sqlalchemy.sql.expression import ColumnElement


class Comparison(abc.ABC):
    @abc.abstractmethod
    def compare(
        self, attr: Union[Column, Any], target: Any
    ) -> Union[BooleanClauseList, "ColumnElement[Boolean]"]:
        """Receives column or function and returns a sqlalchemy comparison"""


class Equal(Comparison):
    def compare(
        self, attr: Union[Column, Any], target: Any
    ) -> Union[BooleanClauseList, "ColumnElement[Boolean]"]:
        return attr == target


class NotEqual(Comparison):
    def compare(
        self, attr: Union[Column, Any], target: Any
    ) -> Union[BooleanClauseList, "ColumnElement[Boolean]"]:
        return attr != target


class Greater(Comparison):
    def compare(
        self, attr: Union[Column, Any], target: Any
    ) -> Union[BooleanClauseList, "ColumnElement[Boolean]"]:
        return attr > target


class GreaterEqual(Comparison):
    def compare(
        self, attr: Union[Column, Any], target: Any
    ) -> Union[BooleanClauseList, "ColumnElement[Boolean]"]:
        return attr >= target


class Lesser(Comparison):
    def compare(
        self, attr: Union[Column, Any], target: Any
    ) -> Union[BooleanClauseList, "ColumnElement[Boolean]"]:
        return attr < target


class LesserEqual(Comparison):
    def compare(
        self, attr: Union[Column, Any], target: Any
    ) -> Union[BooleanClauseList, "ColumnElement[Boolean]"]:
        return attr <= target


class Like(Comparison):
    def compare(
        self, attr: Union[Column, Any], target: Any
    ) -> Union[BooleanClauseList, "ColumnElement[Boolean]"]:
        return attr.like(f"%{target}%")


class InsensitiveLike(Comparison):
    def compare(
        self, attr: Union[Column, Any], target: Any
    ) -> Union[BooleanClauseList, "ColumnElement[Boolean]"]:
        return attr.ilike(f"%{target}%")


class Contains(Comparison):
    def compare(
        self, attr: Union[Column, Any], target: Any
    ) -> Union[BooleanClauseList, "ColumnElement[Boolean]"]:
        return attr.in_(target)


class Excludes(Comparison):
    def compare(
        self, attr: Union[Column, Any], target: Any
    ) -> Union[BooleanClauseList, "ColumnElement[Boolean]"]:
        return attr.not_in(target)


class Null(Comparison):
    def compare(
        self, attr: Union[Column, Any], isnull: bool
    ) -> Union[BooleanClauseList, "ColumnElement[Boolean]"]:
        return attr.is_(None) if isnull else attr.is_not(None)
