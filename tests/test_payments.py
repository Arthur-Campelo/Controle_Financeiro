from http import HTTPStatus

import factory
import factory.fuzzy
import pytest

from controle_financeiro.models import Payment, PaymentCategory
from controle_financeiro.schemas import (
    PaymentPublicListSchema,
    PaymentPublicSchema,
)


class PaymentFactory(factory.Factory):
    class Meta:
        model = Payment

    amount = factory.Faker('pyfloat', positive=True)
    category = factory.fuzzy.FuzzyChoice(PaymentCategory)

    user_id = 1
    group_id = 1


def test_create_payment(client, user, group, token):

    response = client.post(
        '/payments/',
        headers={'Authorization': f'Bearer {token}'},
        json={'amount': 35.0, 'category': 'fixed'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'amount': 35.0,
        'category': 'fixed',
        'user_id': user.id,
        'group_id': group.id,
    }


def test_create_payment_group_not_found(client, user, token):

    response = client.post(
        '/payments/',
        headers={'Authorization': f'Bearer {token}'},
        json={'amount': 35.0, 'category': 'fixed'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Usuário sem grupo para pagamento'}


def test_create_payment_user_whitout_group(client, user, token):

    response = client.post(
        '/payments/',
        headers={'Authorization': f'Bearer {token}'},
        json={'amount': 35.0, 'category': 'fixed'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Usuário sem grupo para pagamento'}


@pytest.mark.asyncio
async def test_fetch_payment_should_return_5(
    client, session, user, group, token
):

    expected_payments = 5

    payments = PaymentFactory.create_batch(
        expected_payments,
        user_id=user.id,
        group_id=group.id,
    )

    session.add_all(payments)
    await session.commit()

    response = client.get(
        '/payments', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['payments']) == expected_payments
    assert isinstance(
        PaymentPublicListSchema.model_validate(response.json()),
        PaymentPublicListSchema,
    )


@pytest.mark.asyncio
async def test_fetch_payment_filter_should_return_2(
    client, session, user, group, token
):

    created_payments = 5
    expected_payments = 2

    payments = PaymentFactory.create_batch(
        created_payments,
        user_id=user.id,
        group_id=group.id,
    )

    session.add_all(payments)
    await session.commit()

    query_params = {
        'limit': 2,
        'offset': 1,
    }

    response = client.get(
        '/payments/',
        headers={'Authorization': f'Bearer {token}'},
        params=query_params,
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['payments']) == expected_payments
    assert isinstance(
        PaymentPublicListSchema.model_validate(response.json()),
        PaymentPublicListSchema,
    )


@pytest.mark.asyncio
async def test_fetch_payment_filter_category_should_return_3(
    client, session, user, group, token
):

    fixed_payments = 3
    variable_payments = 2

    payments = PaymentFactory.create_batch(
        fixed_payments, user_id=user.id, group_id=group.id, category='fixed'
    )
    payments += PaymentFactory.create_batch(
        variable_payments,
        user_id=user.id,
        group_id=group.id,
        category='variable',
    )

    session.add_all(payments)
    await session.commit()

    query_params = {
        'category': 'fixed',
    }

    response = client.get(
        '/payments/',
        headers={'Authorization': f'Bearer {token}'},
        params=query_params,
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['payments']) == fixed_payments
    assert isinstance(
        PaymentPublicListSchema.model_validate(response.json()),
        PaymentPublicListSchema,
    )


@pytest.mark.asyncio
async def test_fetch_payment_by_id(client, session, user, group, token):

    payment = PaymentFactory.create(
        user_id=user.id,
        group_id=group.id,
    )

    session.add(payment)
    await session.commit()

    response = client.get(
        f'/payments/{payment.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert isinstance(
        PaymentPublicSchema.model_validate(response.json()),
        PaymentPublicSchema,
    )


def test_fetch_payment_by_not_found(client, session, user, group, token):

    response = client.get(
        '/payments/404', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_fetch_payment_by_id_incorrect_group(
    client, session, user, token
):

    payment = PaymentFactory.create(
        user_id=user.id,
        group_id=1,
    )

    session.add(payment)
    await session.commit()

    response = client.get(
        f'/payments/{payment.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_patch_payment(client, session, user, group, token):
    payment = PaymentFactory.create(
        user_id=user.id,
        group_id=group.id,
    )
    session.add(payment)
    await session.commit()

    response = client.patch(
        f'/payments/{payment.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'amount': 0.0},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['amount'] == 0.0


def test_patch_payment_not_found(client, token):

    response = client.patch(
        '/payments/404',
        headers={'Authorization': f'Bearer {token}'},
        json={},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_patch_payment_user_incorrect_group(
    client, session, user, token
):
    payment = PaymentFactory.create(
        user_id=user.id,
        group_id=1,
    )
    session.add(payment)
    await session.commit()

    response = client.patch(
        f'/payments/{payment.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_delete_payment(client, session, user, group, token):
    payment = PaymentFactory.create(
        user_id=user.id,
        group_id=group.id,
    )

    session.add(payment)
    await session.commit()

    response = client.delete(
        f'/payments/{payment.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_payment_not_found(client, group, token):

    response = client.delete(
        '/payments/404',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_delete_incorrect_group(client, session, user, token):
    payment = PaymentFactory.create(
        user_id=user.id,
        group_id=1,
    )

    session.add(payment)
    await session.commit()

    response = client.delete(
        f'/payments/{payment.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
