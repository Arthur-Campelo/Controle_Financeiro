from datetime import date
from typing import Annotated

from fastapi import Path
from pydantic import BaseModel, ConfigDict, EmailStr, Field

Id = Annotated[int, Path(gt=0)]


class Token(BaseModel):
    access_token: str
    token_type: str


class FilterPage(BaseModel):
    offset: int = Field(ge=0, default=0)
    limit: int = Field(ge=0, default=10)


# User
class UserPublicSchema(BaseModel):
    id: Id
    username: str
    email: EmailStr
    birth_date: date

    model_config = ConfigDict(from_attributes=True)


class UserPrivateSchema(BaseModel):
    username: str
    email: EmailStr
    birth_date: date
    password: str


class UserListSchema(BaseModel):
    users: list[UserPublicSchema]


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    birth_date: date | None = None


# Group
class GroupSchema(BaseModel):
    name: str


class GroupPublicSchema(GroupSchema):
    id: Id
    owner_id: Id


class GroupPublicListSchema(BaseModel):
    groups: list[GroupPublicSchema]


class GroupUpdate(BaseModel):
    name: str | None = None
    owner_id: int | None = None
