from http import HTTPStatus

from jwt import decode

from controle_financeiro.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    get_password_hash,
    verify_password,
)


def test_jwt():
    data = {'test': 'test'}

    token = create_access_token(data)
    decoded = decode(token, SECRET_KEY, algorithms=ALGORITHM)

    assert data['test'] == decoded['test']
    assert 'exp' in decoded


def test_verify_password():
    password = 'test'
    hashed_password = get_password_hash(password)

    assert verify_password(password, hashed_password)


def test_jwt_invalid_token(client):
    response = client.get(
        '/users/', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Credenciais inválidas'


def test_jwt_invalid_claim(client):

    invalid_access_token = create_access_token(data={'invalid': 'invalid'})

    response = client.get(
        '/users/', headers={'Authorization': f'Bearer {invalid_access_token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Credenciais inválidas'


def test_jwt_invalid_user(client):

    invalid_access_token = create_access_token(data={'sub': 'invalid@gmail'})

    response = client.get(
        '/users/', headers={'Authorization': f'Bearer {invalid_access_token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Credenciais inválidas'
