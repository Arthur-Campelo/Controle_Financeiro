from http import HTTPStatus

from controle_financeiro.database import get_session
from controle_financeiro.schemas import UserPublicSchema


def test_get_session_real():
    session_generator = get_session()
    session = next(session_generator)
    assert session is not None
    session.close()


def test_create_user(client):

    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@gmail.com',
            'birth_date': '2026-03-27',
            'password': 'test',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'alice',
        'email': 'alice@gmail.com',
        'birth_date': '2026-03-27',
    }


def test_create_user_integrity(client, user):

    response = client.post(
        '/users/',
        json={
            'username': user.username,
            'email': user.email,
            'birth_date': '2026-03-27',
            'password': 'teste',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT


def test_fetch_users(client):

    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_fetch_users_with_user(client, user):

    user_public = UserPublicSchema.model_validate(user).model_dump(mode='json')

    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_public]}


def test_fetch_user(client, user):

    user_public = UserPublicSchema.model_validate(user).model_dump(mode='json')

    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_public


def test_fetch_user_unprocessable_content(client):

    response = client.get('/users/0')

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_fetch_user_not_found(client):

    response = client.get('/users/2')

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_user(client, user):

    response = client.put(
        '/users/1',
        json={
            'user_id': 1,
            'username': 'bob',
            'password': 'test',
            'email': 'bob@gmail.com',
            'birth_date': '2026-03-27',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'bob',
        'email': 'bob@gmail.com',
        'birth_date': '2026-03-27',
    }


def test_update_user_integrity(client, user):

    client.post(
        '/users/',
        json={
            'username': 'teste',
            'password': 'teste',
            'email': 'teste@gmail.com',
            'birth_date': '2026-03-27',
        },
    )

    response = client.put(
        '/users/1',
        json={
            'user_id': 1,
            'username': 'teste',
            'password': 'teste',
            'email': 'teste@gmail.com',
            'birth_date': '2026-03-27',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT


def test_update_user_unprocessable_content(client):
    response = client.put(
        '/users/0',
        json={
            'user_id': 1,
            'username': 'bob',
            'password': 'test',
            'email': 'bob@gmail.com',
            'birth_date': '2026-03-27',
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_update_user_not_found(client):
    response = client.put(
        '/users/1',
        json={
            'user_id': 1,
            'username': 'bob',
            'password': 'test',
            'email': 'bob@gmail.com',
            'birth_date': '2026-03-27',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user(client, user):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_user_unprocessable_content(client, user):
    response = client.delete('/users/0')

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_delete_user_not_found(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.NOT_FOUND
