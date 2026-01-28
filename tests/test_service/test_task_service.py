import datetime

import pytest
from sqlalchemy import select

from app.db.models import Task
from app.schemes.task import CreateTask, TaskFilter, UpdateTask
from app.security.errors import AuthorizationError
from app.services.task import TaskService


@pytest.mark.asyncio
async def test_create_task(db_session, create_user):
    created_at = datetime.datetime.now()
    user = await create_user()
    expected_task = Task(
        id=1,
        title="Название задачи",
        description="Описание задачи",
        assignee_id=user.id,
        status="To Do",
        created_at=created_at,
        updated_at=created_at,
    )
    task_data = CreateTask(
        title="Название задачи",
        description="Описание задачи",
    )
    task_service = TaskService()

    task = await task_service.create_task(user, task_data)

    assert task.id == expected_task.id
    assert task.title == expected_task.title
    assert task.description == expected_task.description
    assert task.assignee_id == user.id
    assert task.status == expected_task.status
    assert task.created_at.date() == created_at.date()
    assert task.updated_at.date() == created_at.date()
    assert task.closed_at is None
    assert task.started_work_at is None


@pytest.mark.asyncio
async def test_get_task(db_session, create_task, create_user):
    user = await create_user()
    expected_task = await create_task(assignee_id=user.id)
    task_service = TaskService()

    task = await task_service.get_task(user, 1)

    assert task.id == expected_task.id
    assert task.title == expected_task.title
    assert task.description == expected_task.description
    assert task.assignee_id == user.id
    assert task.status == expected_task.status
    assert task.created_at == task.created_at
    assert task.updated_at == task.updated_at
    assert task.closed_at == task.closed_at
    assert task.started_work_at == task.started_work_at


@pytest.mark.asyncio
async def test_delete_task(db_session, create_task, create_user):
    task_id = 1
    user = await create_user()
    await create_task(assignee_id=user.id)
    task_service = TaskService()

    await task_service.delete_task(task_id, user)

    async with db_session as session:
        result = await session.execute(select(Task).filter_by(id=task_id))

        result = result.scalars().first()

    assert result is None


@pytest.mark.asyncio
async def test_delete_task_with_not_enough_user_permissions(
    db_session, create_task, create_user
):
    task_id = 1
    user1 = await create_user()
    user2 = await create_user()
    await create_task(assignee_id=user1.id)
    task_service = TaskService()

    with pytest.raises(AuthorizationError) as excinfo:
        await task_service.delete_task(task_id, user2)

    assert (
        "403: Задача c id=1 принадлежит другому пользователю и не может быть удалена."  # noqa: E501
        == str(excinfo.value)
    )


@pytest.mark.asyncio
async def test_delete_task_with_not_found_task(db_session, create_user):
    task_id = 2
    user = await create_user(role="ADMIN")
    task_service = TaskService()

    with pytest.raises(ValueError) as excinfo:
        await task_service.delete_task(task_id, user)

    assert "Задача c id=2 не найдена." == str(excinfo.value)


@pytest.mark.asyncio
async def test_update_task(db_session, create_task, create_user):
    task_id = 1
    user = await create_user()
    await create_task(assignee_id=user.id)
    task_service = TaskService()
    update_data = UpdateTask(
        title="Новое название",
        description="Новое описание",
        assignee_id=1,
        status="In Progress",
    )

    task = await task_service.update_task(
        task_id, user, **update_data.model_dump()
    )

    assert task.id == task_id
    assert task.title == update_data.title
    assert task.description == update_data.description
    assert task.assignee_id == update_data.assignee_id
    assert task.status == update_data.status


@pytest.mark.asyncio
async def test_update_task_with_not_enough_user_permissions(
    db_session, create_task, create_user
):
    task_id = 1
    user = await create_user()
    user1 = await create_user()
    await create_task(assignee_id=user.id)
    task_service = TaskService()
    update_data = UpdateTask(
        title="Новое название",
        description="Новое описание",
        assignee_id=1,
        status="In Progress",
    )

    with pytest.raises(AuthorizationError) as excinfo:
        await task_service.update_task(
            task_id, user1, **update_data.model_dump()
        )

    assert (
        "403: Задача c id=1 принадлежит другому пользователю и не может быть обновлена."  # noqa: E501
        == str(excinfo.value)
    )


@pytest.mark.asyncio
async def test_update_task_with_not_found_task(
    db_session, create_task, create_user
):
    task_id = 2
    user = await create_user()
    await create_task(assignee_id=user.id)
    task_service = TaskService()
    update_data = UpdateTask(
        title="Новое название",
        description="Новое описание",
        assignee_id=1,
        status="In Progress",
    )

    with pytest.raises(ValueError) as excinfo:
        await task_service.update_task(
            task_id, user, **update_data.model_dump()
        )

    assert "Задача c id=2 не найдена." == str(excinfo.value)


@pytest.mark.parametrize(
    "skip,limit,sort_by,ascending,filter,expected_count,expected_last_task_id",
    [
        (
            0,
            5,
            "id",
            True,
            TaskFilter(),
            5,
            5,
        ),
        (
            3,
            3,
            "id",
            True,
            TaskFilter(),
            2,
            5,
        ),
        (
            0,
            5,
            "id",
            False,
            TaskFilter(),
            5,
            1,
        ),
        (
            0,
            5,
            "id",
            False,
            TaskFilter(title="Тестовое название"),
            1,
            1,
        ),
        (
            0,
            5,
            "id",
            False,
            TaskFilter(status="In Progress"),
            1,
            1,
        ),
        (
            0,
            5,
            "id",
            False,
            TaskFilter(assignee_id=1),
            5,
            1,
        ),
        (
            0,
            5,
            "id",
            False,
            TaskFilter(created_at=datetime.date(2026, 1, 1)),
            0,
            None,
        ),
        (
            0,
            5,
            "id",
            False,
            TaskFilter(closed_at=datetime.date(2026, 1, 1)),
            0,
            None,
        ),
    ],
    ids=[
        "test with default parameters",
        "test with skip and limit",
        "test with desc sorting by id",
        "test with filter by title",
        "test with filter by status",
        "test with filter by assignee_id",
        "test with filter by created_at",
        "test with filter by closed_at",
    ],
)
@pytest.mark.asyncio
async def test_get_users(
    db_session,
    create_multiple_task,
    create_user,
    skip,
    limit,
    sort_by,
    ascending,
    filter,
    expected_count,
    expected_last_task_id,
):
    async with db_session as session:
        user = await create_user()
        task = Task(
            title="Тестовое название",
            description="Тестовое описание",
            assignee_id=user.id,
            status="In Progress",
            created_at=datetime.datetime.now(),
            closed_at=datetime.datetime.now(),
        )

        session.add(task)
        await session.commit()

    await create_multiple_task(4, user.id)
    task_service = TaskService()

    tasks = await task_service.get_tasks(
        skip, limit, sort_by, ascending, filter, user
    )

    assert len(tasks) == expected_count

    if expected_last_task_id is not None:
        last_task = tasks[-1]
        assert last_task.id == expected_last_task_id


@pytest.mark.asyncio
async def test_get_tasks_with_not_found_sort_field(
    db_session,
    create_multiple_task,
    create_user,
):
    sort_by = "test_field"
    async with db_session as session:
        user = await create_user()
        task = Task(
            title="Тестовое название",
            description="Тестовое описание",
            assignee_id=user.id,
            status="In Progress",
            created_at=datetime.datetime.now(),
            closed_at=datetime.datetime.now(),
        )
        filter = TaskFilter()

        session.add(task)
        await session.commit()

    await create_multiple_task(4, user.id)
    task_service = TaskService()

    with pytest.raises(AttributeError) as excinfo:
        await task_service.get_tasks(0, 5, sort_by, True, filter, user)

    assert "У задачи нет поля 'test_field'." == str(excinfo.value)
