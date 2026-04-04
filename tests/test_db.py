from dataclasses import asdict
from datetime import date

from sqlalchemy import select

from controle_financeiro.models import User


def test_create_user(session, mock_db_time):

    with mock_db_time(model=User) as time:
        new_user = User(
            username='alice',
            email='alice@example.com',
            password='password',
            birth_date=date(2026, 3, 27),
        )

        session.add(new_user)
        session.commit()

        user = session.scalar(select(User).where(User.username == 'alice'))

        assert asdict(user) == {
            'id': 1,
            'username': 'alice',
            'email': 'alice@example.com',
            'birth_date': date(2026, 3, 27),
            'password': 'password',
            'created_at': time,
            'updated_at': time,
        }