import datetime
from http import HTTPStatus

import pytest

from app.db.models import UserRoles, Task
from app.schemes.task import TaskFilter
from app.security.auth import auth_service


@pytest.mark.parametrize(
    "query_data, current_user_role, expected_status, expected_result",
    [
        (
                {
                    "title": "Название задачи",
                    "description": "Описание задачи",
                },
                UserRoles.USER.value,
                HTTPStatus.CREATED,
                {
                    'assignee_id': 1,
                    'closed_at': None,
                    'description': 'Описание задачи',
                    'id': 1,
                    'started_work_at': None,
                    'status': 'To Do',
                    'title': 'Название задачи',
                    'updated_at': datetime.datetime.now(),
                    'created_at': datetime.datetime.now(),
                }
        ),
    ],
    ids=[
        "succeed create task",
    ],
)
@pytest.mark.asyncio
async def test_create_task(
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
        "/api/v1/tasks/",
        json=query_data,
    )
    result = response.json()

    assert response.status_code == expected_status

    if response.status_code in (HTTPStatus.CREATED,):
        expected_updated_at = expected_result.pop("updated_at")
        result_updated_at = datetime.datetime.fromisoformat(
            result.pop("updated_at")
        )
        expected_created_at = expected_result.pop("created_at")
        result_created_at = datetime.datetime.fromisoformat(
            result.pop("created_at")
        )

        assert expected_created_at.date() == result_created_at.date()
        assert expected_updated_at.date() == result_updated_at.date()

    assert result == expected_result


@pytest.mark.parametrize(
    "query_data, current_user_role, expected_status, expected_result",
    [
        (
                1,
                UserRoles.USER.value,
                HTTPStatus.FORBIDDEN,
                {
                    'detail': 'Задача c id=1 принадлежит другому пользователю и не может быть просмотрена.'
                }
        ),
        (
                1,
                UserRoles.ADMIN.value,
                HTTPStatus.OK,
                {
                    'assignee_id': 1,
                    'closed_at': None,
                    'description': 'Описание задачи',
                    'id': 1,
                    'started_work_at': None,
                    'status': 'To Do',
                    'title': 'Название задачи',
                    'updated_at': datetime.datetime.now(),
                    'created_at': datetime.datetime.now(),
                }
        ),
        (
                2,
                UserRoles.USER.value,
                HTTPStatus.OK,
                {
                    'assignee_id': 2,
                    'closed_at': None,
                    'description': 'Описание задачи 1',
                    'id': 2,
                    'started_work_at': None,
                    'status': 'To Do',
                    'title': 'Название задачи 1',
                    'updated_at': datetime.datetime.now(),
                    'created_at': datetime.datetime.now(),
                }
        ),
        (
                3,
                UserRoles.ADMIN.value,
                HTTPStatus.NOT_FOUND,
                {
                    'detail': 'Задача c id=3 не найдена.'
                }
        ),
    ],
    ids=[
        "failed get other task info with user role",
        "succeed get other task with admin role",
        "succeed get task with user role",
        "failed get task info with admin role: task not found",
    ],
)
@pytest.mark.asyncio
async def test_get_task(
        app_client,
        test_engine,
        create_user,
        create_task,
        query_data,
        current_user_role,
        expected_status,
        expected_result
):
    user1 = await create_user()
    await create_task(
        title='Название задачи',
        description='Описание задачи',
        assignee_id=user1.id
    )
    user = await create_user(role=current_user_role)
    await create_task(
        title='Название задачи 1',
        description='Описание задачи 1',
        assignee_id=user.id
    )
    app_client.app.dependency_overrides[
        auth_service.get_current_user] = lambda: user

    response = app_client.get(
        f"/api/v1/tasks/{query_data}",
    )
    result = response.json()

    assert response.status_code == expected_status

    if response.status_code in (HTTPStatus.OK,):
        expected_updated_at = expected_result.pop("updated_at")
        result_updated_at = datetime.datetime.fromisoformat(
            result.pop("updated_at")
        )
        expected_created_at = expected_result.pop("created_at")
        result_created_at = datetime.datetime.fromisoformat(
            result.pop("created_at")
        )

        assert expected_created_at.date() == result_created_at.date()
        assert expected_updated_at.date() == result_updated_at.date()

    assert result == expected_result


@pytest.mark.parametrize(
    "query_data, current_user_role, expected_status, expected_result",
    [
        (
                3,
                UserRoles.USER.value,
                HTTPStatus.NOT_FOUND,
                {
                    'detail': 'Задача c id=3 не найдена.'
                }
        ),
        (
                1,
                UserRoles.USER.value,
                HTTPStatus.FORBIDDEN,
                {
                    'detail': 'Задача c id=1 принадлежит другому пользователю и не может быть удалена.'
                }
        ),
        (
                2,
                UserRoles.USER.value,
                HTTPStatus.NO_CONTENT,
                None,
        ),
        (
                1,
                UserRoles.ADMIN.value,
                HTTPStatus.NO_CONTENT,
                None,
        ),
    ],
    ids=[
        "failed delete task with user role: task not found",
        "failed delete other task with user role",
        "succeed delete task with user role",
        "succeed delete other task with admin role",
    ],
)
@pytest.mark.asyncio
async def test_delete_task(
        app_client,
        test_engine,
        create_user,
        create_task,
        query_data,
        current_user_role,
        expected_status,
        expected_result
):
    user1 = await create_user()
    await create_task(
        title='Название задачи',
        description='Описание задачи',
        assignee_id=user1.id
    )
    user = await create_user(role=current_user_role)
    await create_task(
        title='Название задачи 1',
        description='Описание задачи 1',
        assignee_id=user.id
    )
    app_client.app.dependency_overrides[
        auth_service.get_current_user] = lambda: user

    response = app_client.delete(
        f"/api/v1/tasks/{query_data}",
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
                    "title": "Название задачи",
                    "description": "Описание задачи",
                    "status": "To Do"
                },
                UserRoles.USER.value,
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {
                    'detail': [{'ctx': {
                        'expected': "'In Progress', 'Done' or 'Cancelled'"},
                        'input': 'To Do',
                        'loc': ['body', 'status'],
                        'msg': "Input should be 'In Progress', 'Done' or 'Cancelled'",
                        'type': 'literal_error'}]
                }
        ),
        (
                1,
                {
                    "title": "Название задачи",
                    "description": "Описание задачи",
                    "status": "In Progress"
                },
                UserRoles.USER.value,
                HTTPStatus.OK,
                {
                    'assignee_id': 1,
                    'closed_at': None,
                    'created_at': datetime.datetime.now(),
                    'description': 'Описание задачи',
                    'id': 1,
                    'started_work_at': datetime.datetime.now(),
                    'status': 'In Progress',
                    'title': 'Название задачи',
                    'updated_at': datetime.datetime.now(),
                }
        ),
        (
                1,
                {
                    "title": "Название задачи",
                    "status": "In Progress"
                },
                UserRoles.USER.value,
                HTTPStatus.OK,
                {
                    'assignee_id': 1,
                    'closed_at': None,
                    'created_at': datetime.datetime.now(),
                    'description': 'Описание задачи',
                    'id': 1,
                    'started_work_at': datetime.datetime.now(),
                    'status': 'In Progress',
                    'title': 'Название задачи',
                    'updated_at': datetime.datetime.now(),
                }
        ),
        (
                1,
                {
                    "description": "Описание задачи",
                },
                UserRoles.USER.value,
                HTTPStatus.OK,
                {
                    'assignee_id': 1,
                    'closed_at': None,
                    'created_at': datetime.datetime.now(),
                    'description': 'Описание задачи',
                    'id': 1,
                    'started_work_at': None,
                    'status': 'To Do',
                    'title': 'Название задачи',
                    'updated_at': datetime.datetime.now(),

                }
        ),
        (
                2,
                {
                    "title": "",
                    "description": "Описание задачи",
                },
                UserRoles.USER.value,
                HTTPStatus.FORBIDDEN,
                {
                    'detail': 'Задача c id=2 принадлежит другому пользователю и не может быть обновлена.'
                }
        ),
        (
                2,
                {
                    "title": "Название задачи",
                    "description": "Описание задачи",
                },
                UserRoles.ADMIN.value,
                HTTPStatus.OK,
                {
                    'assignee_id': 2,
                    'closed_at': None,
                    'created_at': datetime.datetime.now(),
                    'description': 'Описание задачи',
                    'id': 2,
                    'started_work_at': None,
                    'status': 'To Do',
                    'title': 'Название задачи',
                    'updated_at': datetime.datetime.now(),

                }
        ),
        (
                1,
                {
                    'status': 'Done'
                },
                UserRoles.USER.value,
                HTTPStatus.BAD_REQUEST,
                {
                    'detail': "Задача не может сменить статус с To Do на Done. Доступные варианты: ('In Progress', 'Cancelled')"
                }
        ),

    ],
    ids=[
        "failed update task: bad status",
        "succeed update task",
        "succeed update task without description",
        "failed update task: without title",
        "failed update task: user does not have permissions",
        "succeed update other task with admin role",
        "failed update task: status can not change",
    ],
)
@pytest.mark.asyncio
async def test_update_task(
        app_client,
        test_engine,
        create_user,
        create_task,
        query_data,
        update_data,
        current_user_role,
        expected_status,
        expected_result
):
    user = await create_user(role=current_user_role)
    await create_task(
        title="Название задачи",
        description="Описание задачи",
        assignee_id=user.id
    )
    user1 = await create_user()
    await create_task(
        assignee_id=user1.id
    )
    app_client.app.dependency_overrides[
        auth_service.get_current_user] = lambda: user

    response = app_client.patch(
        f"/api/v1/tasks/{query_data}",
        json=update_data,
    )
    result = response.json()

    assert response.status_code == expected_status

    if response.status_code in (HTTPStatus.OK,):
        expected_updated_at = expected_result.pop("updated_at")
        result_updated_at = datetime.datetime.fromisoformat(
            result.pop("updated_at")
        )
        expected_created_at = expected_result.pop("created_at")
        result_created_at = datetime.datetime.fromisoformat(
            result.pop("created_at")
        )

        if result.get("started_work_at"):
            expected_started_work_at = expected_result.pop("started_work_at")
            result_started_work_at = datetime.datetime.fromisoformat(
                result.pop("started_work_at")
            )
            assert expected_started_work_at.date() == result_started_work_at.date()

        assert expected_created_at.date() == result_created_at.date()
        assert expected_updated_at.date() == result_updated_at.date()

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
                UserRoles.USER.value,
                HTTPStatus.OK,
                5,
                7,
                {},
        ),
        (
                None,
                None,
                None,
                None,
                None,
                UserRoles.ADMIN.value,
                HTTPStatus.OK,
                7,
                7,
                {},
        ),
        (
                -1,
                5,
                'id',
                True,
                TaskFilter(),
                UserRoles.USER.value,
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
                TaskFilter(),
                UserRoles.USER.value,
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
                TaskFilter(),
                UserRoles.USER.value,
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
                TaskFilter(),
                UserRoles.USER.value,
                HTTPStatus.BAD_REQUEST,
                None,
                None,
                {
                    'detail': "У задачи нет поля 'some_field'."
                }
        ),
    ],
    ids=[
        "succeed get tasks with default parameters",
        "succeed get other tasks with admin role",
        "failed get tasks: bad skip value lt 0",
        "failed get tasks: bad limit value gt 100",
        "failed get tasks: bad limit value lt 1",
        "failed get tasks: bad sort_by value",
    ],
)
@pytest.mark.asyncio
async def test_get_tasks(
        db_session,
        app_client,
        create_multiple_task,
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
        task1 = Task(
            title="Название задачи",
            description="Описание задачи",
            assignee_id=user.id
        )

        session.add(task1)
        await session.commit()

    user1 = await create_user()
    await create_multiple_task(2, assignee_id=user1.id)
    await create_multiple_task(4, assignee_id=user.id)

    if any([skip, limit, sort_by, ascending, filter]):
        url = f"/api/v1/tasks/?skip={skip}&limit={limit}&sort_by={sort_by}&ascending={ascending}"
    else:
        url = '/api/v1/tasks/'

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
