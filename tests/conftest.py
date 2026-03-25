import pytest
from fastapi.testclient import TestClient

from controle_financeiro.app import app


@pytest.fixture
def client():
    return TestClient(app)
