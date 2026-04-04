from contextlib import contextmanager
from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from controle_financeiro.app import app
from controle_financeiro.database import get_session
from controle_financeiro.models import User, table_registry
from controle_financeiro.security import get_password_hash
from controle_financeiro.settings import Settings


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override

        yield client

        app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def user(session: Session):
    password = 'alicealice'
    user = User(
        username='alice',
        email='alice@gmail.com',
        password=get_password_hash(password),
        birth_date=date(2026, 3, 5),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

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
