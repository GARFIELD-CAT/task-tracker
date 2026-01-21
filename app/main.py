import asyncio
import logging

import uvicorn
from fastapi import FastAPI

from api.v1.task import task_router
from app.api.v1.auth import auth_router
from app.api.v1.user import user_router

from core.settings import settings
from services.main_service import main_service

logging.basicConfig(level=settings.logger_level)
app = FastAPI(
    title=settings.project_name,
    description="Документация API сервиса",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(task_router, prefix="/api/v1/tasks")
app.include_router(user_router, prefix="/api/v1/users")
app.include_router(auth_router, prefix="/api/v1/auth")


if __name__ == "__main__":
    asyncio.run(main_service.init_db())

    uvicorn.run(
        app="main:app",
        host=settings.project_host,
        port=settings.project_port,
        reload=True,
    )