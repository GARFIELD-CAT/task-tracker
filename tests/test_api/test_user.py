import datetime
from http import HTTPStatus

import pytest

from app.db.models import UserRoles, User
from app.schemes.user import UserFilter
from app.security.auth import auth_service


@pytest.mark.parametrize(
    "current_user_role, expected_status, expected_result",
    [
        (
                UserRoles.ADMIN.value,
                HTTPStatus.OK,
                {
                    'created_at': datetime.datetime.now(),
                    'email': 'test1@gmail.com',
                    'first_name': 'Денис',
                    'id': 1,
                    'is_active': True,
                    'last_name': 'Ягунов',
                    'role': 'ADMIN'
                }
        ),
        (
                UserRoles.USER.value,
                HTTPStatus.OK,
                {
                    'created_at': datetime.datetime.now(),
                    'email': 'test1@gmail.com',
                    'first_name': 'Денис',
                    'id': 1,
                    'is_active': True,
                    'last_name': 'Ягунов',
                    'role': 'USER'
                }
        ),
        (
                'testRole',
                HTTPStatus.FORBIDDEN,
                {
                    'detail': 'У вас нет достаточных прав для доступа к этому ресурсу.'
                }
        ),
    ],
    ids=[
        "succeed get user info with admin role",
        "succeed get user info with user role",
        "failed get user info with some new role",
    ],
)
@pytest.mark.asyncio
async def test_read_users_me(
        app_client,
        test_engine,
        create_user,
        current_user_role,
        expected_status,
        expected_result
):
    user_data = {
        "email": "test1@gmail.com",
        "password": "testPassword1",
        "first_name": "Денис",
        "last_name": "Ягунов"
    }
    user = await create_user(
        role=current_user_role, **user_data
    )
    app_client.app.dependency_overrides[
        auth_service.get_current_user] = lambda: user

    response = app_client.get(
        "/api/v1/users/me/",
    )
    result = response.json()

    assert response.status_code == expected_status

    if response.status_code in (HTTPStatus.OK,):
        expected_created_at = expected_result.pop("created_at")
        result_created_at = datetime.datetime.fromisoformat(
            result.pop("created_at"))

        assert expected_created_at.date() == result_created_at.date()

    assert result == expected_result


@pytest.mark.parametrize(
    "query_data, current_user_role, expected_status, expected_result",
    [
        (
                {
                    "email": "test1@gmail.com",
                    "password": "testPassword1",
                    "first_name": "Денис",
                    "last_name": "Ягунов"
                },
                UserRoles.ADMIN.value,
                HTTPStatus.CREATED,
                {
                    'created_at': datetime.datetime.now(),
                    'email': 'test1@gmail.com',
                    'first_name': 'Денис',
                    'id': 2,
                    'is_active': True,
                    'last_name': 'Ягунов',
                    'role': 'USER'
                }
        ),
        (
                {
                    "email": "русскиебуквы@gmail.com",
                    "password": "testPassword1",
                    "first_name": "Денис",
                    "last_name": "Ягунов"
                },
                UserRoles.ADMIN.value,
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {
                    'detail': [{'ctx': {'error': {}},
                                'input': 'русскиебуквы@gmail.com',
                                'loc': ['body', 'email'],
                                'msg': 'Value error, Некорректный формат почты. Почта должна '
                                       'состоять только из латинских букв и содержать как минимум '
                                       '1 символ . и @',
                                'type': 'value_error'}]
                }
        ),
        (
                {
                    "email": "test!!!1@gmail.com",
                    "password": "testPassword1",
                    "first_name": "Денис",
                    "last_name": "Ягунов"
                },
                UserRoles.ADMIN.value,
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {
                    'detail': [{'ctx': {'error': {}},
                                'input': 'test!!!1@gmail.com',
                                'loc': ['body', 'email'],
                                'msg': 'Value error, Некорректный формат почты. Почта должна '
                                       'состоять только из латинских букв и содержать как минимум '
                                       '1 символ . и @',
                                'type': 'value_error'}]
                }
        ),
        (
                {
                    "email": "test@gmail.com",
                    "password": "testPa1",
                    "first_name": "Денис",
                    "last_name": "Ягунов"
                },
                UserRoles.ADMIN.value,
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {
                    'detail': [{'ctx': {'min_length': 8},
                                'input': 'testPa1',
                                'loc': ['body', 'password'],
                                'msg': 'String should have at least 8 characters',
                                'type': 'string_too_short'}]
                }
        ),
        (
                {
                    "email": "test@gmail.com",
                    "password": "testPassword",
                    "first_name": "Денис",
                    "last_name": "Ягунов"
                },
                UserRoles.ADMIN.value,
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {
                    'detail': [{'ctx': {'error': {}},
                                'input': 'testPassword',
                                'loc': ['body', 'password'],
                                'msg': 'Value error, Пароль должен содержать не менее 8 символов, '
                                       'включая одну заглавную букву и одну цифру.',
                                'type': 'value_error'}]
                }
        ),
        (
                {
                    "email": "test@gmail.com",
                    "password": "testpassword1",
                    "first_name": "Денис",
                    "last_name": "Ягунов"
                },
                UserRoles.ADMIN.value,
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {
                    'detail': [{'ctx': {'error': {}},
                                'input': 'testpassword1',
                                'loc': ['body', 'password'],
                                'msg': 'Value error, Пароль должен содержать не менее 8 символов, '
                                       'включая одну заглавную букву и одну цифру.',
                                'type': 'value_error'}]
                }
        ),
        (
                {
                    "email": "test@gmail.com",
                    "password": "ТестовыйПароль1",
                    "first_name": "Денис",
                    "last_name": "Ягунов"
                },
                UserRoles.ADMIN.value,
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {
                    'detail': [{'ctx': {'error': {}},
                                'input': 'ТестовыйПароль1',
                                'loc': ['body', 'password'],
                                'msg': 'Value error, Пароль должен содержать не менее 8 символов, '
                                       'включая одну заглавную букву и одну цифру.',
                                'type': 'value_error'}]
                }
        ),
        (
                {
                    "email": "test1@gmail.com",
                    "password": "testPassword1",
                    "first_name": "Денис",
                    "last_name": "Ягунов"
                },
                UserRoles.USER.value,
                HTTPStatus.FORBIDDEN,
                {
                    'detail': 'У вас нет достаточных прав для доступа к этому ресурсу.'
                }
        ),
        (
                {
                    "email": "t@y.ru",
                    "password": "testPassword1",
                    "first_name": "Денис",
                    "last_name": "Ягунов"
                },
                UserRoles.ADMIN.value,
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {
                    'detail': [{'ctx': {'min_length': 7},
                                'input': 't@y.ru',
                                'loc': ['body', 'email'],
                                'msg': 'String should have at least 7 characters',
                                'type': 'string_too_short'}]
                }
        ),
    ],
    ids=[
        "succeed create user",
        "failed create user: email has Cyrillic characters",
        "failed create user: email has special characters",
        "failed create user: password less than 8 characters",
        "failed create user: password does not contain 1 digit",
        "failed create user: password does not contain 1 uppercase character",
        "failed create user: password has Cyrillic characters",
        "failed create user: user does not have permissions",
        "failed create user: email less than 7 characters",
    ],
)
@pytest.mark.asyncio
async def test_create_user(
        app_client,
        test_engine,
        create_user,
        query_data,
        current_user_role,
        expected_status,
        expected_result
):
    user = await create_user(role=current_user_role)
    app_client.app.dependency_overrides[
        auth_service.get_current_user] = lambda: user

    response = app_client.post(
        "/api/v1/users/",
        json=query_data,
    )
    result = response.json()

    assert response.status_code == expected_status

    if response.status_code in (HTTPStatus.CREATED,):
        expected_created_at = expected_result.pop("created_at")
        result_created_at = datetime.datetime.fromisoformat(
            result.pop("created_at"))

        assert expected_created_at.date() == result_created_at.date()

    assert result == expected_result


@pytest.mark.parametrize(
    "query_data, current_user_role, expected_status, expected_result",
    [
        (
                1,
                UserRoles.USER.value,
                HTTPStatus.FORBIDDEN,
                {
                    'detail': 'У вас нет достаточных прав для доступа к этому ресурсу.'
                }
        ),
        (
                1,
                UserRoles.ADMIN.value,
                HTTPStatus.OK,
                {
                    'created_at': datetime.datetime.now(),
                    'email': 'test1@gmail.com',
                    'first_name': 'Денис',
                    'id': 1,
                    'is_active': True,
                    'last_name': 'Ягунов',
                    'role': 'USER'
                }
        ),
        (
                2,
                UserRoles.USER.value,
                HTTPStatus.FORBIDDEN,
                {
                    'detail': 'У вас нет достаточных прав для доступа к этому ресурсу.'
                }
        ),
        (
                3,
                UserRoles.ADMIN.value,
                HTTPStatus.NOT_FOUND,
                {
                    'detail': 'Пользователь c id=3 не найден.'
                }
        ),
    ],
    ids=[
        "failed get user info with user role",
        "succeed get user info with admin role",
        "failed get other user info with user role",
        "failed get user info with admin role: user not found",
    ],
)
@pytest.mark.asyncio
async def test_get_user(
        app_client,
        test_engine,
        create_user,
        query_data,
        current_user_role,
        expected_status,
        expected_result
):
    user_data = {
        "email": "test1@gmail.com",
        "password": "testPassword1",
        "first_name": "Денис",
        "last_name": "Ягунов"
    }
    await create_user(**user_data)
    user = await create_user(role=current_user_role)
    app_client.app.dependency_overrides[
        auth_service.get_current_user] = lambda: user

    response = app_client.get(
        f"/api/v1/users/{query_data}",
    )
    result = response.json()

    assert response.status_code == expected_status

    if response.status_code in (HTTPStatus.OK,):
        expected_created_at = expected_result.pop("created_at")
        result_created_at = datetime.datetime.fromisoformat(
            result.pop("created_at"))

        assert expected_created_at.date() == result_created_at.date()

    assert result == expected_result


@pytest.mark.parametrize(
    "query_data, current_user_role, expected_status, expected_result",
    [
        (
                3,
                UserRoles.ADMIN.value,
                HTTPStatus.NOT_FOUND,
                {
                    'detail': 'Пользователь c id=3 не найден.'
                }
        ),
        (
                2,
                UserRoles.USER.value,
                HTTPStatus.FORBIDDEN,
                {
                    'detail': 'Запись пользователя c id=2 принадлежит другому пользователю и не может быть удалена.'
                }
        ),
        (
                1,
                UserRoles.USER.value,
                HTTPStatus.NO_CONTENT,
                None,
        ),

        (
                2,
                UserRoles.ADMIN.value,
                HTTPStatus.NO_CONTENT,
                None,
        ),

    ],
    ids=[
        "failed delete user with admin role: user not found",
        "failed delete other user with user role",
        "succeed delete user with user role",
        "succeed delete user with admin role",
    ],
)
@pytest.mark.asyncio
async def test_delete_user(
        app_client,
        test_engine,
        create_user,
        query_data,
        current_user_role,
        expected_status,
        expected_result
):
    user = await create_user(role=current_user_role)
    await create_user()

    app_client.app.dependency_overrides[
        auth_service.get_current_user] = lambda: user

    response = app_client.delete(
        f"/api/v1/users/{query_data}",
    )

    assert response.status_code == expected_status

    if response.status_code not in (HTTPStatus.NO_CONTENT,):
        result = response.json()

        assert result == expected_result


@pytest.mark.parametrize(
    "query_data, update_data, current_user_role, expected_status, expected_result",
    [
        (
                1,
                {
                    "email": "test1@gmail.com",
                    "password": "testPassword1",
                    "first_name": "Денис",
                    "last_name": "Ягунов"
                },
                UserRoles.USER.value,
                HTTPStatus.OK,
                {
                    'created_at': datetime.datetime.now(),
                    'email': 'test1@gmail.com',
                    'first_name': 'Денис',
                    'id': 1,
                    'is_active': True,
                    'last_name': 'Ягунов',
                    'role': 'USER'
                }
        ),
        (
                2,
                {
                    "email": "test1@gmail.com",
                    "password": "testPassword1",
                    "first_name": "Денис",
                    "last_name": "Ягунов"
                },
                UserRoles.ADMIN.value,
                HTTPStatus.OK,
                {
                    'created_at': datetime.datetime.now(),
                    'email': 'test1@gmail.com',
                    'first_name': 'Денис',
                    'id': 2,
                    'is_active': True,
                    'last_name': 'Ягунов',
                    'role': 'USER'
                }
        ),
        (
                1,
                {
                    "email": "русскиебуквы@gmail.com",
                    "password": "testPassword1",
                    "first_name": "Денис",
                    "last_name": "Ягунов"
                },
                UserRoles.USER.value,
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {
                    'detail': [{'ctx': {'error': {}},
                                'input': 'русскиебуквы@gmail.com',
                                'loc': ['body', 'email'],
                                'msg': 'Value error, Некорректный формат почты. Почта должна '
                                       'состоять только из латинских букв и содержать как минимум '
                                       '1 символ . и @',
                                'type': 'value_error'}]
                }
        ),
        (
                1,
                {
                    "email": "test!!!1@gmail.com",
                    "password": "testPassword1",
                    "first_name": "Денис",
                    "last_name": "Ягунов"
                },
                UserRoles.USER.value,
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {
                    'detail': [{'ctx': {'error': {}},
                                'input': 'test!!!1@gmail.com',
                                'loc': ['body', 'email'],
                                'msg': 'Value error, Некорректный формат почты. Почта должна '
                                       'состоять только из латинских букв и содержать как минимум '
                                       '1 символ . и @',
                                'type': 'value_error'}]
                }
        ),
        (
                1,
                {
                    "email": "test@gmail.com",
                    "password": "testPa1",
                    "first_name": "Денис",
                    "last_name": "Ягунов"
                },
                UserRoles.USER.value,
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {
                    'detail': [{'ctx': {'min_length': 8},
                                'input': 'testPa1',
                                'loc': ['body', 'password'],
                                'msg': 'String should have at least 8 characters',
                                'type': 'string_too_short'}]
                }
        ),
        (
                1,
                {
                    "email": "test@gmail.com",
                    "password": "testPassword",
                    "first_name": "Денис",
                    "last_name": "Ягунов"
                },
                UserRoles.USER.value,
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {
                    'detail': [{'ctx': {'error': {}},
                                'input': 'testPassword',
                                'loc': ['body', 'password'],
                                'msg': 'Value error, Пароль должен содержать не менее 8 символов, '
                                       'включая одну заглавную букву и одну цифру.',
                                'type': 'value_error'}]
                }
        ),
        (
                1,
                {
                    "email": "test@gmail.com",
                    "password": "testpassword1",
                    "first_name": "Денис",
                    "last_name": "Ягунов"
                },
                UserRoles.ADMIN.value,
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {
                    'detail': [{'ctx': {'error': {}},
                                'input': 'testpassword1',
                                'loc': ['body', 'password'],
                                'msg': 'Value error, Пароль должен содержать не менее 8 символов, '
                                       'включая одну заглавную букву и одну цифру.',
                                'type': 'value_error'}]
                }
        ),
        (
                1,
                {
                    "email": "test@gmail.com",
                    "password": "ТестовыйПароль1",
                    "first_name": "Денис",
                    "last_name": "Ягунов"
                },
                UserRoles.ADMIN.value,
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {
                    'detail': [{'ctx': {'error': {}},
                                'input': 'ТестовыйПароль1',
                                'loc': ['body', 'password'],
                                'msg': 'Value error, Пароль должен содержать не менее 8 символов, '
                                       'включая одну заглавную букву и одну цифру.',
                                'type': 'value_error'}]
                }
        ),
        (
                2,
                {
                    "email": "test1@gmail.com",
                    "password": "testPassword1",
                    "first_name": "Денис",
                    "last_name": "Ягунов"
                },
                UserRoles.USER.value,
                HTTPStatus.FORBIDDEN,
                {
                    'detail': 'Запись пользователя c id=2 принадлежит другому пользователю и не может быть обновлена.'}
        ),
        (
                1,
                {
                    "email": "t@y.ru",
                    "password": "testPassword1",
                    "first_name": "Денис",
                    "last_name": "Ягунов"
                },
                UserRoles.USER.value,
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {
                    'detail': [{'ctx': {'min_length': 7},
                                'input': 't@y.ru',
                                'loc': ['body', 'email'],
                                'msg': 'String should have at least 7 characters',
                                'type': 'string_too_short'}]
                }
        ),
        (
                3,
                {
                    "email": "test1@gmail.com",
                    "password": "testPassword1",
                    "first_name": "Денис",
                    "last_name": "Ягунов"
                },
                UserRoles.ADMIN.value,
                HTTPStatus.NOT_FOUND,
                {
                    'detail': 'Пользователь c id=3 не найден.'
                }
        ),
    ],
    ids=[
        "succeed update user with user role",
        "succeed update other user with admin role",
        "failed update user: email has Cyrillic characters",
        "failed update user: email has special characters",
        "failed update user: password less than 8 characters",
        "failed update user: password does not contain 1 digit",
        "failed update user: password does not contain 1 uppercase character",
        "failed update user: password has Cyrillic characters",
        "failed update user: user does not have permissions",
        "failed update user: email less than 7 characters",
        "failed update user: user not found",
    ],
)
@pytest.mark.asyncio
async def test_update_user(
        app_client,
        test_engine,
        create_user,
        query_data,
        update_data,
        current_user_role,
        expected_status,
        expected_result
):
    user = await create_user(role=current_user_role)
    await create_user()
    app_client.app.dependency_overrides[
        auth_service.get_current_user] = lambda: user

    response = app_client.patch(
        f"/api/v1/users/{query_data}",
        json=update_data,
    )
    result = response.json()

    assert response.status_code == expected_status

    if response.status_code in (HTTPStatus.OK,):
        expected_created_at = expected_result.pop("created_at")
        result_created_at = datetime.datetime.fromisoformat(
            result.pop("created_at"))

        assert expected_created_at.date() == result_created_at.date()

    assert result == expected_result


@pytest.mark.parametrize(
    "skip, limit, sort_by, ascending, filter, current_user_role, expected_status, expected_count, expected_last_user_id, expected_result",
    [
        (
                None,
                None,
                None,
                None,
                None,
                UserRoles.ADMIN.value,
                HTTPStatus.OK,
                6,
                6,
                {},
        ),
        (
                0,
                5,
                'id',
                True,
                UserFilter(),
                UserRoles.USER.value,
                HTTPStatus.FORBIDDEN,
                None,
                None,
                {
                    'detail': 'У вас нет достаточных прав для доступа к этому ресурсу.'
                },
        ),
        (
                -1,
                5,
                'id',
                True,
                UserFilter(),
                UserRoles.ADMIN.value,
                HTTPStatus.UNPROCESSABLE_ENTITY,
                None,
                None,
                {
                    'detail': [{'ctx': {'ge': 0},
                                'input': '-1',
                                'loc': ['query', 'skip'],
                                'msg': 'Input should be greater than or equal to 0',
                                'type': 'greater_than_equal'}]
                },
        ),
        (
                0,
                101,
                'id',
                True,
                UserFilter(),
                UserRoles.ADMIN.value,
                HTTPStatus.UNPROCESSABLE_ENTITY,
                None,
                None,
                {
                    'detail': [{'ctx': {'lt': 101},
                                'input': '101',
                                'loc': ['query', 'limit'],
                                'msg': 'Input should be less than 101',
                                'type': 'less_than'}]
                }
        ),
        (
                0,
                0,
                'id',
                True,
                UserFilter(),
                UserRoles.ADMIN.value,
                HTTPStatus.UNPROCESSABLE_ENTITY,
                None,
                None,
                {
                    'detail': [{'ctx': {'gt': 0},
                                'input': '0',
                                'loc': ['query', 'limit'],
                                'msg': 'Input should be greater than 0',
                                'type': 'greater_than'}]
                }
        ),
        (
                0,
                5,
                'some_field',
                True,
                UserFilter(),
                UserRoles.ADMIN.value,
                HTTPStatus.BAD_REQUEST,
                None,
                None,
                {
                    'detail': "У пользователя нет поля 'some_field'."
                }
        ),
    ],
    ids=[
        'succeed get users with default parameters',
        "failed get users: user does not have permissions",
        "failed get users: bad skip value lt 0",
        "failed get users: bad limit value gt 100",
        "failed get users: bad limit value lt 1",
        "failed get users: bad sort_by value",
    ],
)
@pytest.mark.asyncio
async def test_get_users(
        db_session,
        app_client,
        create_multiple_users,
        create_user,
        skip,
        limit,
        sort_by,
        ascending,
        filter,
        current_user_role,
        expected_status,
        expected_count,
        expected_last_user_id,
        expected_result,
):
    user = await create_user(role=current_user_role)
    app_client.app.dependency_overrides[
        auth_service.get_current_user] = lambda: user

    async with db_session as session:
        user1 = User(
            email='test1@example.com',
            last_name='Mask1',
            first_name='Elon1',
            created_at=datetime.datetime.now(),
        )

        session.add(user1)
        await session.commit()

    await create_multiple_users(4)

    if any([skip, limit, sort_by, ascending, filter]):
        url = f"/api/v1/users/?skip={skip}&limit={limit}&sort_by={sort_by}&ascending={ascending}"
    else:
        url = '/api/v1/users/'

    response = app_client.get(url)
    result = response.json()

    assert response.status_code == expected_status

    if response.status_code != HTTPStatus.OK:
        assert result == expected_result

    if expected_count is not None:
        assert len(result) == expected_count

    if expected_last_user_id is not None:
        last_user = result[-1]
        assert last_user.get('id') == expected_last_user_id
