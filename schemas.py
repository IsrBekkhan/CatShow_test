from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


class Breeds(BaseModel):
    breeds: List[str]

    model_config = ConfigDict(from_attributes=True)


class CatForm(BaseModel):
    color: str = Field(
        ...,
        description="Цвет котёнка",
        max_length=50,
        min_length=1,
    )
    age: int = Field(
        ...,
        description="Возраст (полных месяцев) котёнка",
        ge=0,
    )
    description: str = Field(
        "",
        description="Описание котёнка",
        max_length=500,
        min_length=0,
    )
    breed: str = Field(
        ...,
        description="Порода котёнка",
        max_length=50,
        min_length=1,
    )

    model_config = ConfigDict(from_attributes=True)


class CatDetail(CatForm):
    id: int


class CatBrief(CatDetail):
    age: Optional[int] = Field(..., exclude=True)
    description: Optional[str] = Field(..., exclude=True)


class CatChangeForm(BaseModel):
    color: Optional[str] = Field(
        None,
        description="Цвет котёнка",
        max_length=50,
        min_length=1,
    )
    age: Optional[int] = Field(
        None,
        description="Возраст (полных месяцев) котёнка",
        ge=0,
    )
    description: Optional[str] = Field(
        None,
        description="Описание котёнка",
        max_length=500,
        min_length=0,
    )
    breed: Optional[str] = Field(
        None,
        description="Порода котёнка",
        max_length=50,
        min_length=1,
    )




