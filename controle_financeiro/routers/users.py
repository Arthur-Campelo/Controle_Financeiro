from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from controle_financeiro.database import get_session
from controle_financeiro.models import User
from controle_financeiro.schemas import (
    FilterPage,
    UserListSchema,
    UserPrivateSchema,
    UserPublicSchema,
)
from controle_financeiro.security import (
    get_current_user,
    get_password_hash,
)

router = APIRouter(prefix='/users', tags=['users'])

AsyncSession = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
FilterPage = Annotated[FilterPage, Query()]


@router.get('/', status_code=HTTPStatus.OK, response_model=UserListSchema)
async def fetch_users(
    session: AsyncSession,
    current_user: CurrentUser,
    filter_page: FilterPage,
):
    users = await session.scalars(
        select(User).limit(filter_page.limit).offset(filter_page.offset)
    )
    return {'users': users}


@router.get(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublicSchema,
)
async def fetch_user(
    user_id: int,
    session: AsyncSession,
    current_user: CurrentUser,
):
    if not user_id:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_CONTENT)

    db_user = await session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    return db_user


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=UserPublicSchema
)
async def create_user(user: UserPrivateSchema, session: AsyncSession):

    db_user = await session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    user.password = get_password_hash(user.password)

    db_user = User(**user.model_dump())

    session.add(db_user)

    try:
        await session.commit()
    except IntegrityError:
        raise HTTPException(
            detail='Username or Email already exists',
            status_code=HTTPStatus.CONFLICT,
        )

    return db_user


@router.put(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublicSchema,
)
async def update_user(
    user_id: int,
    user: UserPrivateSchema,
    session: AsyncSession,
    current_user: CurrentUser,
):
    if not user_id:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_CONTENT)

    if current_user.id != user_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)

    try:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = get_password_hash(user.password)
        current_user.birth_date = user.birth_date

        await session.commit()

    except IntegrityError:
        raise HTTPException(
            detail='Username or Email already exists',
            status_code=HTTPStatus.CONFLICT,
        )

    await session.refresh(current_user)
    return current_user


@router.delete('/{user_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_user(
    user_id: int,
    session: AsyncSession,
    current_user: CurrentUser,
):
    if not user_id:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_CONTENT)

    if current_user.id != user_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)

    await session.delete(current_user)
    await session.commit()
