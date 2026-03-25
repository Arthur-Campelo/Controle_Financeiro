from http import HTTPStatus

from fastapi import FastAPI, HTTPException

from controle_financeiro.schemas import (
    UserListSchema,
    UserPrivateSchema,
    UserPublicSchema,
)

app = FastAPI()

database = []  # Simulando um banco de dados com uma lista


# users
@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserListSchema)
def fetch_users():
    return {'users': database}


@app.post(
    '/users/', status_code=HTTPStatus.CREATED, response_model=UserPublicSchema
)
def create_user(user: UserPrivateSchema):
    user_with_id = {**user.model_dump(), 'id': len(database) + 1}
    database.append(user_with_id)
    return user


@app.put(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublicSchema,
)
def update_user(user_id: int, user: UserPublicSchema):

    if user_id > len(database) or user_id < 1:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    user_with_id = {**user.model_dump(), 'id': user_id}
    database[user_id - 1] = user_with_id

    return user_with_id


@app.delete(
    '/users/{user_id}',
    status_code=HTTPStatus.NO_CONTENT,
)
def delete_user(user_id: int):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    database.pop(user_id-1)
