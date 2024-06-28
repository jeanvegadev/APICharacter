from typing import Any
from pydantic import (
    BaseModel,
    field_validator,
    PositiveInt,
)


class CharacterBase(BaseModel):
    id: int
    name: str
    height: PositiveInt
    mass: PositiveInt
    hair_color: str
    skin_color: str
    eye_color: str
    birth_year: PositiveInt

    @field_validator('name', 'hair_color', 'skin_color', 'eye_color')
    def check_not_empty(cls, value: Any) -> Any:
        if value == "":
            raise ValueError('Must not be empty')
        return value


class Character(CharacterBase):
    class Config:
        # orm_mode = True
        from_attributes = True


class GetAll(BaseModel):
    id: int
    name: str
    height: int
    mass: int
    eye_color: str
    birth_year: int

    class Config:
        from_attributes = True
