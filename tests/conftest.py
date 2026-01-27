import os

import pytest_asyncio
from dotenv import load_dotenv
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from app.db.models import Base, Task, User
from app.main import app

load_dotenv()


@pytest_asyncio.fixture(scope="session")
async def faker():
    """Faker с русской локалью"""

    return Faker(locale="ru_RU")


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Подключение к тестовой БД"""

    database_url = os.getenv("TEST_DATABASE_URL")
    engine = create_async_engine(database_url)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine):
    """Сессия с откатом транзакций"""
    session_maker = sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    session = session_maker()

    yield session

    session.close()


@pytest_asyncio.fixture(scope="session")
def app_client():
    with TestClient(app) as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def user_data_generator(faker):
    """Генератор тестовых пользователей"""

    async def _generate_user_data(**overrides):
        base_data = {
            "email": faker.unique.email(),
            "password": faker.password(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
        }

        return {**base_data, **overrides}

    return _generate_user_data


@pytest_asyncio.fixture(scope="function")
async def create_user(db_session, user_data_generator):
    """Фабрика пользователей с Faker"""

    async def _create_user(**overrides):
        async with db_session as session:
            user_data = await user_data_generator(**overrides)
            user = User(**user_data)

            session.add(user)
            await session.commit()

        return user

    return _create_user


@pytest_asyncio.fixture(scope="function")
async def create_multiple_users(db_session, user_data_generator):
    """Фабрика для создания нескольких пользователей"""

    async def _create_multiple_users(count=5):
        users = []

        async with db_session as session:
            for _ in range(count):
                user_data = await user_data_generator()
                user = User(**user_data)
                users.append(user)

            session.add_all(users)
            await session.commit()

        return users

    return _create_multiple_users


@pytest_asyncio.fixture(scope="function")
async def task_data_generator(faker):
    """Генератор тестовых задач"""

    async def _generate_task_data(**overrides):
        base_data = {
            "title": faker.sentence(nb_words=5),
            "description": faker.text(max_nb_chars=300),
            "assignee_id": None,
            "status": "To Do",
        }

        return {**base_data, **overrides}

    return _generate_task_data


@pytest_asyncio.fixture(scope="function")
async def create_task(db_session, task_data_generator):
    """Фабрика задач с Faker"""

    async def _create_task(**overrides):
        async with db_session as session:
            task_data = await task_data_generator(**overrides)
            task = Task(**task_data)

            db_session.add(task)
            await session.commit()

        return task

    return _create_task


@pytest_asyncio.fixture(scope="function")
async def create_multiple_task(db_session, task_data_generator):
    """Фабрика для создания нескольких задач для пользователя"""

    async def _create_multiple_posts(count=3, assignee_id=None):
        tasks = []

        async with db_session as session:
            for _ in range(count):
                task_data = await task_data_generator(assignee_id=assignee_id)
                task = Task(**task_data)
                db_session.add(task)
                tasks.append(task)

            session.add_all(tasks)
            await session.commit()

        return tasks

    return _create_multiple_posts
