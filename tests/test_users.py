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


def test_fetch_user_not_found(client, token):

    response = client.get(
        '/users/404', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_user(client, user, token):

    response = client.patch(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'password': 'test',
            'email': 'bob@gmail.com',
            'birth_date': '2026-03-27',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': 'bob',
        'email': 'bob@gmail.com',
        'birth_date': '2026-03-27',
    }


def test_update_user_patch_email_only(client, user, token):

    response = client.patch(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'email': 'bob@gmail.com',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': user.username,
        'email': 'bob@gmail.com',
        'birth_date': user.birth_date.isoformat(),
    }


def test_update_user_forbidden(client, token, other_user):
    response = client.patch(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'username': 'bob'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_update_user_integrity(client, user, other_user, token):
    response = client.patch(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': other_user.username,
            'email': other_user.email,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT


# def test_update_user_not_found(client, token):
#     response = client.patch(
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


def test_delete_user_forbidden(client, other_user, token):

    response = client.delete(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


# def test_delete_user_not_found(client):
#     response = client.delete('/users/1')

#     assert response.status_code == HTTPStatus.NOT_FOUND
