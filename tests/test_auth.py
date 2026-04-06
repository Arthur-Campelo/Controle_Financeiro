from http import HTTPStatus

import pytest

from controle_financeiro.settings import Settings

settings = Settings()


@pytest.mark.asyncio
async def test_login_for_access_token(client, user):
    response = client.post(
        'auth/token/',
        data={'username': user.email, 'password': user.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


@pytest.mark.asyncio
async def test_login_for_access_token_not_found(client, user):
    response = client.post(
        'auth/token/',
        data={'username': 'wrong@email', 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_login_for_access_token_unauthorized(client, user):
    response = client.post(
        'auth/token/',
        data={'username': user.email, 'password': 'wrong_password'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_token_expired(client, expired_token):
    response = client.get(
        '/users/', headers={'Authorization': f'Bearer {expired_token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_refresh_token(client, token):
    response = client.post(
        'auth/refresh_token/', headers={'Authorization': f'Bearer {token}'}
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'Bearer'


def test_refresh_token_expired(client, expired_token):
    response = client.post(
        '/auth/refresh_token/',
        headers={'Authorization': f'Bearer {expired_token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
