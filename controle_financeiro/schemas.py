from pydantic import BaseModel, EmailStr


class Message(BaseModel):
    message: str


class UserPublicSchema(BaseModel):
    username: str
    email: EmailStr


class UserPrivateSchema(UserPublicSchema):
    password: str


class UserDB(UserPrivateSchema):
    id: int


class UserListSchema(BaseModel):
    users: list[UserPublicSchema]
