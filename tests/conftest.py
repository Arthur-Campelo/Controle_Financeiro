from contextlib import contextmanager
from datetime import date, datetime, timedelta

import factory
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from freezegun import freeze_time
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from controle_financeiro.app import app
from controle_financeiro.database import get_session
from controle_financeiro.models import User, table_registry
from controle_financeiro.security import get_password_hash
from controle_financeiro.settings import Settings
from tests.test_groups import GroupFactory


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as Session:
        yield Session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest_asyncio.fixture
async def user(session: AsyncSession):
    password = 'alicealice'

    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    # salvando apenas em execução a senha limpa para testes
    user.clean_password = password  # type: ignore

    return user


# todo use or delete this fixture
@pytest_asyncio.fixture
async def group(session: AsyncSession, user):

    group = GroupFactory(owner_id=user.id)

    session.add(group)
    await session.flush()

    user.group_id = group.id
    await session.commit()

    return group


@pytest_asyncio.fixture
async def other_user(session: AsyncSession):
    password = 'bobbob'

    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    # salvando apenas em execução a senha limpa para testes
    user.clean_password = password  # type: ignore

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        'auth/token/',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
    )

    return response.json()['access_token']


@pytest.fixture
def expired_token(client, user, settings):
    time = datetime.now()
    past_expired_token_time = time - timedelta(
        days=settings.ACCESS_TOKEN_EXPIRE_DAYS,
        minutes=1,  # Garantia para comparações >= ou >
    )

    with freeze_time(past_expired_token_time):
        response = client.post(
            '/auth/token',
            data={
                'username': user.email,
                'password': user.clean_password,
            },
        )

    return response.json()['access_token']


@pytest.fixture
def settings():
    return Settings()


@contextmanager
def _mock_db_time(*, model, time=datetime(2025, 5, 20)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.sequence(lambda n: f'test{n}')
    birth_date = date(2026, 3, 5)
    email = factory.lazy_attribute(lambda obj: f'{obj.username}@email.com')
    password = factory.lazy_attribute(lambda obj: f'{obj.username}123')
