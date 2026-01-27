from http import HTTPStatus

import pytest


@pytest.mark.parametrize(
    "expected_status, tasks_count, expected_result",
    [
        (
                HTTPStatus.OK,
                None,
                '<h1>Нет данных для отображения. Заполните базу данных.</h1>'
        ),
        (
                HTTPStatus.OK,
                10,
                "<title>Отчет по задачам</title"
        ),
    ],
    ids=[
        "succeed get report: empty database",
        "succeed get report",
    ],
)
@pytest.mark.asyncio
async def test_reports(
        app_client,
        test_engine,
        create_user,
        create_multiple_task,
        expected_status,
        tasks_count,
        expected_result,
):
    user = await create_user()

    if tasks_count is not None:
        await create_multiple_task(tasks_count, assignee_id=user.id)

    response = app_client.get(
        "/api/v1/analytics/reports",
    )
    result = response.text

    assert response.status_code == expected_status
    assert expected_result in result