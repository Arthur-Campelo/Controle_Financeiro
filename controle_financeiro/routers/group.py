from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from controle_financeiro.database import get_session
from controle_financeiro.models import Group, User
from controle_financeiro.schemas import (
    FilterPage,
    GroupPublicListSchema,
    GroupPublicSchema,
    GroupSchema,
    GroupUpdate,
    Id,
)
from controle_financeiro.security import (
    get_current_user,
)

router = APIRouter(prefix='/groups', tags=['groups'])

AsyncSession = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
FilterPage = Annotated[FilterPage, Query()]


@router.get(
    '/', status_code=HTTPStatus.OK, response_model=GroupPublicListSchema
)
async def fetch_groups(
    session: AsyncSession,
    current_user: CurrentUser,
    filter_page: FilterPage,
):
    response = await session.scalars(
        select(Group).offset(filter_page.offset).limit(filter_page.limit)
    )

    return {'groups': response}


@router.get(
    '/{group_id}', status_code=HTTPStatus.OK, response_model=GroupPublicSchema
)
async def fetch_group(
    group_id: Id,
    session: AsyncSession,
    current_user: CurrentUser,
):
    response = await session.scalar(select(Group).where(Group.id == group_id))

    if not response:
        raise HTTPException(HTTPStatus.NOT_FOUND)

    return response


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=GroupPublicSchema
)
async def create_group(
    session: AsyncSession,
    current_user: CurrentUser,
    group: GroupSchema,
):
    db_group = Group(name=group.name, owner_id=current_user.id)

    session.add(db_group)

    await session.commit()
    await session.refresh(db_group)

    return db_group


@router.patch(
    '/{group_id}', status_code=HTTPStatus.OK, response_model=GroupPublicSchema
)
async def patch_group(
    group_id: Id,
    group: GroupUpdate,
    session: AsyncSession,
    current_user: CurrentUser,
):
    db_group = await session.scalar(select(Group).where(Group.id == group_id))

    if not db_group:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Grupo não encotrado'
        )

    if db_group.owner_id != current_user.id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)

    if group.owner_id is not None:
        new_owner_exists = await session.scalar(
            select(User).where(User.id == group.owner_id)
        )
        if not new_owner_exists:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Novo dono do grupo não encotrado',
            )

    for key, value in group.model_dump(exclude_unset=True).items():
        setattr(db_group, key, value)

    await session.commit()
    await session.refresh(db_group)

    return db_group


@router.delete('/{group_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_group(
    group_id: Id,
    session: AsyncSession,
    current_user: CurrentUser,
):
    group = await session.scalar(select(Group).where(Group.id == group_id))

    if not group:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    if current_user.id != group.owner_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)

    await session.delete(group)
    await session.commit()
