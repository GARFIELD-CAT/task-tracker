import asyncio
import logging

import uvicorn
from fastapi import FastAPI

from api.v1.task import task_router

from core.settings import settings
from services.main_service import main_service

logging.basicConfig(level=settings.logger_level)
app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
)

app.include_router(task_router, prefix="/api/v1/tasks")


if __name__ == "__main__":
    asyncio.run(main_service.init_db())

    uvicorn.run(
        app="main:app",
        host=settings.project_host,
        port=settings.project_port,
        reload=True,
    )