from controle_financeiro.database import get_session


def test_get_session_real():
    session_generator = get_session()
    session = next(session_generator)
    assert session is not None
    session.close()
