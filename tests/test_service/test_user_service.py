import datetime

import pytest

from sqlalchemy import select

from app.db.models import User
from app.schemes.user import CreateUser, UpdateUser, UserFilter
from app.security.auth import AuthService
from app.security.errors import AuthorizationError
from app.services.user import UserService


@pytest.mark.asyncio
async def test_create_user(db_session):
    created_at=datetime.datetime.now()

    expected_user = User(
        id=1,
        email='test@example.com',
        password='Password1',
        first_name='Test',
        last_name='User',
        is_active=True,
        created_at=created_at,
        role='USER',
    )

    user_data = CreateUser(
        email='test@example.com',
        password='Password1',
        first_name='Test',
        last_name='User'
    )
    user_service = UserService()
    auth_service = AuthService()

    user = await user_service.create_user(user_data)
    verified_password = auth_service.verify_password(expected_user.password, user.password)

    assert user.id == expected_user.id
    assert user.email == expected_user.email
    assert verified_password is True
    assert user.first_name == expected_user.first_name
    assert user.last_name == expected_user.last_name
    assert user.is_active == expected_user.is_active
    assert user.created_at.date() == created_at.date()
    assert user.role == expected_user.role


@pytest.mark.asyncio
async def test_create_user_with_same_email(db_session, create_user):
    await create_user(email='test@example.com')

    user_data = CreateUser(
        email='test@example.com',
        password='Password1',
        first_name='Test',
        last_name='User'
    )

    user_service = UserService()

    with pytest.raises(ValueError) as excinfo:
        await user_service.create_user(user_data)

    assert "Пользователь с email='test@example.com' уже был создан." == str(excinfo.value)


@pytest.mark.asyncio
async def test_get_user_by_id(db_session, create_user):
    expected_user = await create_user()
    user_service = UserService()

    user = await user_service.get_user_by_id(1)

    assert user.id == expected_user.id
    assert user.email == expected_user.email
    assert user.first_name == expected_user.first_name
    assert user.last_name == expected_user.last_name
    assert user.is_active == expected_user.is_active
    assert user.created_at == expected_user.created_at
    assert user.role == expected_user.role

@pytest.mark.asyncio
async def test_get_user_by_email(db_session, create_user):
    expected_user = await create_user(email='test@example.com')
    user_service = UserService()

    user = await user_service.get_user_by_email('test@example.com')

    assert user.email == expected_user.email
    assert user.first_name == expected_user.first_name
    assert user.last_name == expected_user.last_name
    assert user.is_active == expected_user.is_active
    assert user.created_at == expected_user.created_at
    assert user.role == expected_user.role


@pytest.mark.asyncio
async def test_delete_user(db_session, create_user):
    user_id = 1
    user = await create_user()
    user_service = UserService()

    await user_service.delete_user(user_id, user)

    async with db_session as session:
        result = await session.execute(
            select(User).filter_by(id=user_id)
        )

        result = result.scalars().first()

    assert result is None


@pytest.mark.asyncio
async def test_delete_with_not_enough_user_permissions(db_session, create_user):
    user_id = 2
    user = await create_user()
    user_service = UserService()

    with pytest.raises(AuthorizationError) as excinfo:
        await user_service.delete_user(user_id, user)

    assert "403: Запись пользователя c id=2 принадлежит другому пользователю и не может быть удалена." == str(excinfo.value)


@pytest.mark.asyncio
async def test_delete_with_not_found_user(db_session, create_user):
    user_id = 2
    user = await create_user(role='ADMIN')
    user_service = UserService()

    with pytest.raises(ValueError) as excinfo:
        await user_service.delete_user(user_id, user)

    assert "Пользователь c id=2 не найден." == str(excinfo.value)

@pytest.mark.asyncio
async def test_update_user(db_session, create_user):
    user_id = 1
    user = await create_user()
    user_service = UserService()
    update_data = UpdateUser(
        email='new_user@test.com',
        password='NewPassword1',
        first_name='New_Test',
        last_name='New_User',
    )

    user = await user_service.update_user(user_id, user, **update_data.model_dump())

    assert user.id == user_id
    assert user.email == update_data.email
    assert user.first_name == update_data.first_name
    assert user.last_name == update_data.last_name


@pytest.mark.asyncio
async def test_update_with_not_enough_user_permissions(db_session, create_user):
    user_id = 2
    update_data = UpdateUser(
        email='new_user@test.com',
        password='NewPassword1',
        first_name='New_Test',
        last_name='New_User',
    )
    user = await create_user()
    user_service = UserService()

    with pytest.raises(AuthorizationError) as excinfo:
        await user_service.update_user(
            user_id, user, **update_data.model_dump()
        )

    assert "403: Запись пользователя c id=2 принадлежит другому пользователю и не может быть обновлена." == str(excinfo.value)


@pytest.mark.asyncio
async def test_update_with_not_found_user(db_session, create_user):
    user_id = 2
    user = await create_user(role='ADMIN')
    update_data = UpdateUser(
        email='new_user@test.com',
        password='NewPassword1',
        first_name='New_Test',
        last_name='New_User',
    )
    user_service = UserService()

    with pytest.raises(ValueError) as excinfo:
        await user_service.update_user(
            user_id, user, **update_data.model_dump()
        )

    assert "Пользователь c id=2 не найден." == str(excinfo.value)


@pytest.mark.parametrize(
    "skip,limit,sort_by,ascending,filter,expected_count, expected_last_user_id",
    [
        (
            0,
            5,
            'id',
            True,
            UserFilter(),
            5,
            5,
        ),
        (
            3,
            3,
            'id',
            True,
            UserFilter(),
            2,
            5,
        ),
        (
            0,
            5,
            'id',
            False,
            UserFilter(),
            5,
            1,
        ),
        (
            0,
            5,
            'id',
            False,
            UserFilter(
                email='test1@example.com'
            ),
            1,
            1,
        ),
        (
            0,
            5,
            'id',
            False,
            UserFilter(
                first_name='Elon1'
            ),
            1,
            1,
        ),
        (
            0,
            5,
            'id',
            False,
            UserFilter(
                last_name='Mask1'
            ),
            1,
            1,
        ),
        (
            0,
            5,
            'id',
            False,
            UserFilter(
                created_at=datetime.date(2026, 1, 1)
            ),
            0,
            None,
        )
    ],
    ids=[
        'test with default parameters',
        'test with skip and limit',
        'test with desc sorting by id',
        'test with filter by email',
        'test with filter by first_name',
        'test with filter by last_name',
        'test with filter by created_at',
    ],
)
@pytest.mark.asyncio
async def test_get_users(
    db_session,
    create_multiple_users,
    create_user,
    skip,
    limit,
    sort_by,
    ascending,
    filter,
    expected_count,
    expected_last_user_id,
):
    async with db_session as session:
        user = User(
            email='test1@example.com',
            last_name='Mask1',
            first_name='Elon1',
            created_at=datetime.datetime.now(),
        )

        session.add(user)
        await session.commit()

    await create_multiple_users(4)
    user_service = UserService()

    users = await user_service.get_users(skip, limit, sort_by, ascending, filter)

    assert len(users) == expected_count

    if expected_last_user_id is not None:
        last_user = users[-1]
        assert last_user.id == expected_last_user_id


@pytest.mark.asyncio
async def test_get_users_with_not_found_sort_field(
    db_session,
    create_multiple_users,
    create_user,
):
    sort_by = 'test_field'
    filter = UserFilter()
    async with db_session as session:
        user = User(
            email='test1@example.com',
            last_name='Mask1',
            first_name='Elon1',
            created_at=datetime.datetime.now(),
        )

        session.add(user)
        await session.commit()

    await create_multiple_users(4)
    user_service = UserService()

    with pytest.raises(AttributeError) as excinfo:
        await user_service.get_users(0, 5, sort_by, True, filter)

    assert "У пользователя нет поля 'test_field'." == str(excinfo.value)
