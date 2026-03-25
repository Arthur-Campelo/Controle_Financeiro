from http import HTTPStatus


def test_create_user(client):

    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@gmail.com',
            'password': 'test',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'username': 'alice', 'email': 'alice@gmail.com'}


def test_fetch_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [{'username': 'alice', 'email': 'alice@gmail.com'}]
    }


def test_update_user(client):
    response = client.put(
        '/users/1',
        json={'user_id': 1, 'username': 'bob', 'email': 'bob@gmail.com'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'username': 'bob', 'email': 'bob@gmail.com'}


def test_delete_user(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.NO_CONTENT
