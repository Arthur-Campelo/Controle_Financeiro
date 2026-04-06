from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from controle_financeiro.database import get_session
from controle_financeiro.models import User
from controle_financeiro.schemas import Token
from controle_financeiro.security import (
    create_access_token,
    get_current_user,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])

AsyncSession = Annotated[AsyncSession, Depends(get_session)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/token/', response_model=Token)
async def login_for_access_token(
    form_data: OAuth2Form,
    session: AsyncSession,
):
    db_user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Email não cadastrado'
        )

    valid_credentials = verify_password(form_data.password, db_user.password)

    if not valid_credentials:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Senha ou Email incorreto',
        )

    access_token = create_access_token({'sub': db_user.email})

    return {'access_token': access_token, 'token_type': 'Bearer'}


@router.post('/refresh_token/', response_model=Token)
async def refresh_for_new_access_token(
    user: Annotated[User, Depends(get_current_user)],
):
    new_access_token = create_access_token({'sub': user.email})
    return {'access_token': new_access_token, 'token_type': 'Bearer'}
