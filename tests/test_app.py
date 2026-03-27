from http import HTTPStatus


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


def test_fetch_users(client):

    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'username': 'alice',
                'email': 'alice@gmail.com',
                'birth_date': '2026-03-27',
            }
        ]
    }


def test_fetch_user(client):

    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'alice',
        'email': 'alice@gmail.com',
        'birth_date': '2026-03-27',
    }


def test_fetch_user_not_found(client):

    response = client.get('/users/2')

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_user(client):
    response = client.put(
        '/users/1',
        json={
            'user_id': 1,
            'username': 'bob',
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


def test_update_user_not_found(client):
    response = client.put(
        '/users/2',
        json={
            'user_id': 1,
            'username': 'bob',
            'email': 'bob@gmail.com',
            'birth_date': '2026-03-27',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_user_not_found(client):
    response = client.delete('/users/2')

    assert response.status_code == HTTPStatus.NOT_FOUND
