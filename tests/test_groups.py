from http import HTTPStatus

import factory
import pytest

from controle_financeiro.models import Group
from controle_financeiro.schemas import (
    GroupPublicListSchema,
    GroupPublicSchema,
)


class GroupFactory(factory.Factory):
    class Meta:
        model = Group

    name = factory.Faker('text')
    owner_id = 1


def test_create_group(client, user, token):

    response = client.post(
        '/groups/',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'groupTeste'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'name': 'groupTeste',
        'owner_id': user.id,
    }


@pytest.mark.asyncio
async def test_fetch_groups_should_return_5(client, session, user, token):

    expected_groups = 5
    groups = GroupFactory.create_batch(expected_groups, owner_id=user.id)

    session.add_all(groups)
    await session.commit()

    response = client.get(
        '/groups/', headers={'Authorization': f'Bearer {token}'}
    )
    json_response = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(json_response['groups']) == expected_groups
    assert isinstance(
        GroupPublicListSchema.model_validate(json_response),
        GroupPublicListSchema,
    )


@pytest.mark.asyncio
async def test_fetch_group(client, session, user, token):

    group = GroupFactory.create(owner_id=user.id)

    session.add(group)
    await session.commit()

    response = client.get(
        f'/groups/{group.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert isinstance(
        GroupPublicSchema.model_validate(response.json()),
        GroupPublicSchema,
    )


def test_fetch_group_not_found(client, token):

    response = client.get(
        '/groups/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_fetch_groups_should_return_2_filter(
    client, session, user, token
):

    created_groups = 5
    expected_groups = 2

    groups = GroupFactory.create_batch(created_groups, owner_id=user.id)

    session.add_all(groups)
    await session.commit()

    response = client.get(
        '/groups/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )
    json_response = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(json_response['groups']) == expected_groups
    assert isinstance(
        GroupPublicListSchema.model_validate(json_response),
        GroupPublicListSchema,
    )


@pytest.mark.asyncio
async def test_patch_group(session, client, user, token):

    group = GroupFactory.create(owner_id=user.id)
    session.add(group)

    await session.commit()
    await session.refresh(group)

    response = client.patch(
        f'/groups/{group.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'newGroupName'},
    )

    assert response.status_code == HTTPStatus.OK
    assert isinstance(
        GroupPublicSchema.model_validate(response.json()),
        GroupPublicSchema,
    )


@pytest.mark.asyncio
async def test_patch_group_forbidden(session, client, other_user, token):

    group = GroupFactory.create(owner_id=other_user.id)
    session.add(group)

    await session.commit()
    await session.refresh(group)

    response = client.patch(
        f'/groups/{group.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'newGroupName'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_patch_group_not_found(client, token):

    response = client.patch(
        '/groups/404',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'newGroupName'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_patch_group_new_owner(session, client, user, other_user, token):

    group = GroupFactory.create(owner_id=user.id)
    session.add(group)

    await session.commit()
    await session.refresh(group)

    response = client.patch(
        f'/groups/{group.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'owner_id': other_user.id},
    )

    assert response.status_code == HTTPStatus.OK
    assert isinstance(
        GroupPublicSchema.model_validate(response.json()),
        GroupPublicSchema,
    )
    assert response.json()['owner_id'] == other_user.id


@pytest.mark.asyncio
async def test_patch_group_new_owner_not_found(session, client, user, token):

    group = GroupFactory.create(owner_id=user.id)
    session.add(group)

    await session.commit()
    await session.refresh(group)

    response = client.patch(
        f'/groups/{group.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'owner_id': 404},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Novo dono do grupo não encotrado'}


@pytest.mark.asyncio
async def test_delete_group(session, client, user, token):

    group = GroupFactory.create(owner_id=user.id)
    session.add(group)

    await session.commit()
    await session.refresh(group)

    response = client.delete(
        f'/groups/{group.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_group_not_found(client, token):

    response = client.delete(
        '/groups/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_delete_group_not_forbidden(session, client, other_user, token):

    group = GroupFactory.create(owner_id=other_user.id)
    session.add(group)

    await session.commit()
    await session.refresh(group)

    response = client.delete(
        f'/groups/{group.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
