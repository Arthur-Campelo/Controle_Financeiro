from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from controle_financeiro.database import get_session
from controle_financeiro.models import Payment, User
from controle_financeiro.schemas import (
    FilterPage,
    Id,
    PaymentPublicListSchema,
    PaymentPublicSchema,
    PaymentSchema,
)
from controle_financeiro.security import (
    get_current_user,
)

router = APIRouter(prefix='/payments', tags=['Payments'])

AsyncSession = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
FilterPage = Annotated[FilterPage, Query()]

@router.get(
    '/',
    status_code= HTTPStatus.OK,
    response_model= PaymentPublicListSchema,
)
async def fetch_payments(
    session: AsyncSession,
    current_user: CurrentUser,
    filter_page: FilterPage,
):

    response = await session.scalars(
        select(Payment).where(Payment.group_id == current_user.group_id)
        .limit(filter_page.limit).offset(filter_page.offset)
    )

    return { 'payments': response}


@router.get(
    '/{payment_id}',
    status_code= HTTPStatus.OK,
    response_model= PaymentPublicSchema,
)
async def fetch_payment(
    session: AsyncSession,
    current_user: CurrentUser,
    payment_id: Id,
):

    response = await session.scalar(
        select(Payment).where(
            (Payment.id == payment_id) &
            (Payment.group_id == current_user.group_id)
        )
    )

    if not response:
        raise HTTPException(HTTPStatus.NOT_FOUND)

    return response


@router.post(
    '/',
    status_code= HTTPStatus.CREATED,
    response_model=PaymentPublicSchema
)
async def create_payment(
    session: AsyncSession,
    current_user: CurrentUser,
    payment: PaymentSchema,
):
    if not current_user.group_id:
        raise HTTPException(
            status_code= HTTPStatus.UNPROCESSABLE_CONTENT,
            detail=f'{current_user}'
        )

    db_payment = Payment(
        **payment.model_dump(),
        user_id=current_user.id,
        group_id = current_user.group_id
        )

    session.add(db_payment)
    await session.commit()
    await session.refresh(db_payment)

    return db_payment


@router.patch(
    '/{payment_id}',
    status_code= HTTPStatus.OK,
    response_model= PaymentPublicSchema,
)
async def patch_payment(
    session: AsyncSession,
    current_user: CurrentUser,
    payment_id: Id,
    payment: PaymentSchema,
):
    db_payment = await session.scalar(
        select(Payment).where(Payment.id == payment_id)
    )

    if not db_payment:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    if db_payment.group_id != current_user.group_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)

    for key, value in payment.model_dump(exclude_unset=True).items():
            setattr(db_payment, key, value)

    await session.commit()
    await session.refresh(db_payment)

    return db_payment


@router.delete(
    '/{payment_id}',
    status_code= HTTPStatus.OK,
)
async def delete_payment(
    session: AsyncSession,
    current_user: CurrentUser,
    payment_id: Id,
):
    db_payment = await session.scalar(
        select(Payment).where(Payment.id == payment_id)
    )

    if not db_payment:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    if db_payment.group_id != current_user.group_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)

    await session.delete(db_payment)
    await session.commit()
