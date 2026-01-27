import datetime
from http import HTTPStatus

import pytest

from app.security.auth import auth_service


@pytest.mark.parametrize(
    "query_data, expected_status, expected_result",
    [
        (
            {
                "email": "test1@gmail.com",
                "password": "testPassword1",
                "first_name": "Денис",
                "last_name": "Ягунов",
            },
            HTTPStatus.CREATED,
            {
                "created_at": datetime.datetime.now(),
                "email": "test1@gmail.com",
                "first_name": "Денис",
                "id": 1,
                "is_active": True,
                "last_name": "Ягунов",
                "role": "USER",
            },
        ),
        (
            {
                "email": "русскиебуквы@gmail.com",
                "password": "testPassword1",
                "first_name": "Денис",
                "last_name": "Ягунов",
            },
            HTTPStatus.UNPROCESSABLE_ENTITY,
            {
                "detail": [
                    {
                        "ctx": {"error": {}},
                        "input": "русскиебуквы@gmail.com",
                        "loc": ["body", "email"],
                        "msg": "Value error, Некорректный формат почты. Почта должна "
                        "состоять только из латинских букв и содержать как минимум "
                        "1 символ . и @",
                        "type": "value_error",
                    }
                ]
            },
        ),
        (
            {
                "email": "test!!!1@gmail.com",
                "password": "testPassword1",
                "first_name": "Денис",
                "last_name": "Ягунов",
            },
            HTTPStatus.UNPROCESSABLE_ENTITY,
            {
                "detail": [
                    {
                        "ctx": {"error": {}},
                        "input": "test!!!1@gmail.com",
                        "loc": ["body", "email"],
                        "msg": "Value error, Некорректный формат почты. Почта должна "
                        "состоять только из латинских букв и содержать как минимум "
                        "1 символ . и @",
                        "type": "value_error",
                    }
                ]
            },
        ),
        (
            {
                "email": "test@gmail.com",
                "password": "testPa1",
                "first_name": "Денис",
                "last_name": "Ягунов",
            },
            HTTPStatus.UNPROCESSABLE_ENTITY,
            {
                "detail": [
                    {
                        "ctx": {"min_length": 8},
                        "input": "testPa1",
                        "loc": ["body", "password"],
                        "msg": "String should have at least 8 characters",
                        "type": "string_too_short",
                    }
                ]
            },
        ),
        (
            {
                "email": "test@gmail.com",
                "password": "testPassword",
                "first_name": "Денис",
                "last_name": "Ягунов",
            },
            HTTPStatus.UNPROCESSABLE_ENTITY,
            {
                "detail": [
                    {
                        "ctx": {"error": {}},
                        "input": "testPassword",
                        "loc": ["body", "password"],
                        "msg": "Value error, Пароль должен содержать не менее 8 символов, "
                        "включая одну заглавную букву и одну цифру.",
                        "type": "value_error",
                    }
                ]
            },
        ),
        (
            {
                "email": "test@gmail.com",
                "password": "testpassword1",
                "first_name": "Денис",
                "last_name": "Ягунов",
            },
            HTTPStatus.UNPROCESSABLE_ENTITY,
            {
                "detail": [
                    {
                        "ctx": {"error": {}},
                        "input": "testpassword1",
                        "loc": ["body", "password"],
                        "msg": "Value error, Пароль должен содержать не менее 8 символов, "
                        "включая одну заглавную букву и одну цифру.",
                        "type": "value_error",
                    }
                ]
            },
        ),
        (
            {
                "email": "test@gmail.com",
                "password": "ТестовыйПароль1",
                "first_name": "Денис",
                "last_name": "Ягунов",
            },
            HTTPStatus.UNPROCESSABLE_ENTITY,
            {
                "detail": [
                    {
                        "ctx": {"error": {}},
                        "input": "ТестовыйПароль1",
                        "loc": ["body", "password"],
                        "msg": "Value error, Пароль должен содержать не менее 8 символов, "
                        "включая одну заглавную букву и одну цифру.",
                        "type": "value_error",
                    }
                ]
            },
        ),
        (
            {
                "email": "t@y.ru",
                "password": "testPassword1",
                "first_name": "Денис",
                "last_name": "Ягунов",
            },
            HTTPStatus.UNPROCESSABLE_ENTITY,
            {
                "detail": [
                    {
                        "ctx": {"min_length": 7},
                        "input": "t@y.ru",
                        "loc": ["body", "email"],
                        "msg": "String should have at least 7 characters",
                        "type": "string_too_short",
                    }
                ]
            },
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
        "failed create user: email less than 7 characters",
    ],
)
@pytest.mark.asyncio
async def test_register_user(
    app_client, test_engine, query_data, expected_status, expected_result
):
    response = app_client.post(
        "/api/v1/auth/register",
        json=query_data,
    )
    result = response.json()

    assert response.status_code == expected_status

    if response.status_code in (HTTPStatus.CREATED,):
        expected_created_at = expected_result.pop("created_at")
        result_created_at = datetime.datetime.fromisoformat(
            result.pop("created_at")
        )

        assert expected_created_at.date() == result_created_at.date()

    assert result == expected_result


@pytest.mark.parametrize(
    "query_data, expected_status, expected_result",
    [
        (
            {
                "email": "test1@gmail.com",
                "password": "testPassword1",
                "first_name": "Денис",
                "last_name": "Ягунов",
            },
            HTTPStatus.BAD_REQUEST,
            {
                "detail": "Пользователь с email='test1@gmail.com' уже был создан."
            },
        ),
    ],
    ids=[
        "failed create user: email exists",
    ],
)
@pytest.mark.asyncio
async def test_register_user_with_same_email(
    app_client,
    test_engine,
    create_user,
    query_data,
    expected_status,
    expected_result,
):
    await create_user(**query_data)

    response = app_client.post(
        "/api/v1/auth/register",
        json=query_data,
    )
    result = response.json()

    assert response.status_code == expected_status
    assert result == expected_result


@pytest.mark.parametrize(
    "query_data, expected_status, expected_result",
    [
        (
            {
                "email": "test1@gmail.com",
                "password": "testPassword1",
            },
            HTTPStatus.OK,
            {"access_token": "some_token", "token_type": "bearer"},
        ),
        (
            {
                "email": "user@gmail.com",
                "password": "testPassword2",
            },
            HTTPStatus.UNAUTHORIZED,
            {"detail": "Неверное имя пользователя или пароль"},
        ),
    ],
    ids=[
        "succeed generate token",
        "failed generate token: user not found",
    ],
)
@pytest.mark.asyncio
async def test_register_user_with_same_email(
    app_client,
    test_engine,
    create_user,
    query_data,
    expected_status,
    expected_result,
):
    await create_user(
        email="test1@gmail.com",
        password=auth_service.get_password_hash("testPassword1"),
    )

    response = app_client.post(
        "/api/v1/auth/token",
        json=query_data,
    )
    result = response.json()

    assert response.status_code == expected_status

    if response.status_code in (HTTPStatus.OK,):
        assert result.get("token_type") == "bearer"
        assert result.get("access_token") is not None
    else:
        assert result == expected_result
