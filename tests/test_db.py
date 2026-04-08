from dataclasses import asdict
from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from controle_financeiro.models import User

# @pytest.mark.asyncio
# async def test_get_session():
#     async with get_session() as session:
#         assert session is not None


@pytest.mark.asyncio
async def test_create_user(session: AsyncSession, mock_db_time):

    with mock_db_time(model=User) as time:
        new_user = User(
            username='alice',
            email='alice@example.com',
            password='password',
            birth_date=date(2026, 3, 27),
        )

        session.add(new_user)
        await session.commit()

        user = await session.scalar(
            select(User).where(User.username == 'alice')
        )

        assert asdict(user) == {
            'id': 1,
            'username': 'alice',
            'email': 'alice@example.com',
            'birth_date': date(2026, 3, 27),
            'group_id': None,
            'password': 'password',
            'created_at': time,
            'updated_at': time,
        }
