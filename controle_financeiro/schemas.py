from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr


class UserPublicSchema(BaseModel):
    username: str
    email: EmailStr
    birth_date: date

    model_config = ConfigDict(from_attributes=True)


class UserPrivateSchema(UserPublicSchema):
    password: str


class UserListSchema(BaseModel):
    users: list[UserPublicSchema]
