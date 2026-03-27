from datetime import date

from pydantic import BaseModel, EmailStr


class UserPublicSchema(BaseModel):
    username: str
    email: EmailStr
    birth_date: date


class UserPrivateSchema(UserPublicSchema):
    password: str


class UserDB(UserPrivateSchema):
    id: int


class UserListSchema(BaseModel):
    users: list[UserPublicSchema]
