from http import HTTPStatus

from fastapi.testclient import TestClient

from controle_financeiro.app import app

"""" Triple A testing: Arrange, Act, Assert"""

client = TestClient(app)  # Arrange

response = client.get('/')  # act

assert response.json() == {'message': 'Hello World'}  # assert
assert response.status_code == HTTPStatus.OK
