import logging
from http import HTTPStatus

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.services.analytics import analytics_service

analytics_router = APIRouter()
logger = logging.getLogger(__name__)
ANALYTICS_TAG = "Аналитика"


@analytics_router.get(
    "/reports",
    status_code=HTTPStatus.OK,
    response_class=HTMLResponse,
    tags=[ANALYTICS_TAG],
)
async def get_visualization():
    visualization_html = await analytics_service.get_visualization_data()

    if not visualization_html:
        return HTMLResponse(
            "<h1>Нет данных для отображения. Заполните базу данных.</h1>"
        )

    return HTMLResponse(content=visualization_html)
