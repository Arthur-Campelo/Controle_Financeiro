from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr


class UserPublicSchema(BaseModel):
    id: int
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


class Token(BaseModel):
    access_token: str
    token_type: str
