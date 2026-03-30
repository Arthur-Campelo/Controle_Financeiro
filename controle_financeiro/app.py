from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from controle_financeiro.database import get_session
from controle_financeiro.models import User
from controle_financeiro.schemas import (
    UserListSchema,
    UserPrivateSchema,
    UserPublicSchema,
)
from controle_financeiro.security import get_password_hash

app = FastAPI()


# users
@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserListSchema)
def fetch_users(
    session: Session = Depends(get_session),
    limit: int = 10,
    offset: int = 0,
):
    users = session.scalars(select(User).limit(limit).offset(offset))
    return {'users': users}


@app.get(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublicSchema,
)
def fetch_user(user_id: int, session: Session = Depends(get_session)):
    if not user_id:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_CONTENT)

    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    return db_user


@app.post(
    '/users/', status_code=HTTPStatus.CREATED, response_model=UserPublicSchema
)
def create_user(user: UserPrivateSchema, session=Depends(get_session)):

    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    user.password = get_password_hash(user.password)

    db_user = User(**user.model_dump())

    session.add(db_user)

    try:
        session.commit()
    except IntegrityError:
        raise HTTPException(
            detail='Username or Email already exists',
            status_code=HTTPStatus.CONFLICT,
        )

    return db_user


@app.put(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublicSchema,
)
def update_user(
    user_id: int,
    user: UserPrivateSchema,
    session: Session = Depends(get_session),
):
    if not user_id:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_CONTENT)

    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    try:
        db_user.username = user.username
        db_user.email = user.email
        db_user.password = get_password_hash(user.password)
        db_user.birth_date = user.birth_date

        session.commit()

    except IntegrityError:
        raise HTTPException(
            detail='Username or Email already exists',
            status_code=HTTPStatus.CONFLICT,
        )

    session.refresh(db_user)
    return db_user


@app.delete(
    '/users/{user_id}',
    status_code=HTTPStatus.NO_CONTENT,
)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    if not user_id:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_CONTENT)

    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    session.delete(db_user)
    session.commit()
