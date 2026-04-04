from http import HTTPStatus

from controle_financeiro.schemas import UserPublicSchema


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
        'id': 1,
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


def test_fetch_users(client, user, token):

    user_public = UserPublicSchema.model_validate(user).model_dump(mode='json')

    response = client.get(
        '/users/', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_public]}


def test_fetch_user(client, user, token):

    user_public = UserPublicSchema.model_validate(user).model_dump(mode='json')

    response = client.get(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_public


def test_fetch_user_unprocessable_content(client, token):

    response = client.get(
        '/users/0', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_fetch_user_not_found(client, token):

    response = client.get(
        '/users/404', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_user(client, user, token):

    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
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
        'id': 1,
        'username': 'bob',
        'email': 'bob@gmail.com',
        'birth_date': '2026-03-27',
    }


def test_update_user_forbidden(client, token):

    other_user = client.post(
        '/users/',
        json={
            'username': 'test',
            'email': 'test@gmail.com',
            'birth_date': '2026-03-27',
            'password': 'test',
        },
    )

    other_user_id = other_user.json()['id']

    response = client.put(
        f'/users/{other_user_id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'password': 'test',
            'email': 'bob@gmail.com',
            'birth_date': '2026-03-27',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_update_user_integrity(client, user, token):

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
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'teste',
            'password': 'teste',
            'email': 'teste@gmail.com',
            'birth_date': '2026-03-27',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT


def test_update_user_unprocessable_content(client, user, token):
    response = client.put(
        '/users/0',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'password': 'test',
            'email': 'bob@gmail.com',
            'birth_date': '2026-03-27',
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


# def test_update_user_not_found(client, token):
#     response = client.put(
#         '/users/404',
#         headers={'Authorization': f'Bearer {token}'},
#         json={
#             'user_id': 404,
#             'username': 'bob',
#             'password': 'test',
#             'email': 'bob@gmail.com',
#             'birth_date': '2026-03-27',
#         },
#     )

#     assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_user_forbidden(client, token):
    other_user = client.post(
        '/users/',
        json={
            'username': 'test',
            'email': 'test@gmail.com',
            'birth_date': '2026-03-27',
            'password': 'test',
        },
    )

    other_user_id = other_user.json()['id']

    response = client.delete(
        f'/users/{other_user_id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_delete_user_unprocessable_content(client, token):
    response = client.delete(
        '/users/0',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


# def test_delete_user_not_found(client):
#     response = client.delete('/users/1')

#     assert response.status_code == HTTPStatus.NOT_FOUND
