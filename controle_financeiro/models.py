from datetime import date, datetime
from enum import Enum
from typing import List

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

table_registry = registry()


class PaymentCategory(str, Enum):
    fixed = 'fixed'
    variable = 'variable'


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    birth_date: Mapped[date]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

    payments: Mapped[List['Payment']] = relationship(
        init=False,
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    group_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            'groups.id',
            ondelete='SET NULL',
            use_alter=True,
            name='fk_user_group_id',
        ),
        default=None,
    )


@table_registry.mapped_as_dataclass
class Group:
    __tablename__ = 'groups'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]

    users: Mapped[List['User']] = relationship(
        init=False,
        lazy='selectin',
        foreign_keys=[User.group_id],
    )

    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'))


@table_registry.mapped_as_dataclass
class Payment:
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    amount: Mapped[float]
    category: Mapped[PaymentCategory]

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey('groups.id', ondelete='CASCADE')
    )
