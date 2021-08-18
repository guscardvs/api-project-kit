import re
from typing import TYPE_CHECKING, Generic, TypeVar

from pydantic import BaseModel, create_model

_to_camel_exp = re.compile("_([a-zA-Z])")


class DTO(BaseModel):
    class Config:
        allow_population_by_field_name = True
        allow_mutation = False
        use_enum_values = True

        @classmethod
        def alias_generator(cls, string):
            return re.sub(_to_camel_exp, lambda match: match[1].upper(), string)


if TYPE_CHECKING:
    DTO_T = TypeVar("DTO_T", bound=DTO)

    class _EmbedArray(Generic[DTO_T]):
        data: list[DTO_T]


def embed_array(dto: "type[DTO_T]", mod: str) -> "_EmbedArray[DTO_T]":
    return create_model(f"{dto.__qualname__}EmbedArray", __base__=DTO, __module__=mod, data=(list[dto], ...))  # type: ignore
