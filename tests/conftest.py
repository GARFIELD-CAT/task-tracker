import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.db.models import Base, UserRoles, TaskStatuses, User, Task
from app.services.task import TaskService
from app.services.user import UserService

load_dotenv()


@pytest.fixture(scope='session')
def faker():
    """Faker с русской локалью"""

    return Faker(locale='ru_RU')


@pytest_asyncio.fixture(scope='function')
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


@pytest_asyncio.fixture(scope='function')
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


@pytest.fixture
def user_data_generator(faker):
    """Генератор тестовых пользователей"""

    def _generate_user_data(**overrides):
        base_data = {
            'email': faker.unique.email(),
            'password': faker.password(),
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
        }

        return {**base_data, **overrides}
    return _generate_user_data


@pytest_asyncio.fixture(scope='function')
async def create_user(db_session, user_data_generator):
    """Фабрика пользователей с Faker"""

    async def _create_user(**overrides):
        async with db_session as session:
            user_data = user_data_generator(**overrides)
            user = User(**user_data)

            session.add(user)
            await session.commit()

        return user
    return _create_user


@pytest_asyncio.fixture(scope='function')
async def create_multiple_users(db_session, user_data_generator):
    """Фабрика для создания нескольких пользователей"""

    async def _create_multiple_users(count=5):
        users = []

        async with db_session as session:
            for _ in range(count):
                user_data = user_data_generator()
                user = User(**user_data)
                users.append(user)

            session.add_all(users)
            await session.commit()

        return users
    return _create_multiple_users



@pytest.fixture
def create_task(db_session, task_data_generator):
    """Фабрика задач с Faker"""

    def _create_task(**overrides):
        task_data = task_data_generator(**overrides)
        task = Task(**task_data)
        db_session.add(task)
        db_session.commit()

        return task

    return _create_task


#
#
# @pytest.fixture
# def create_multiple_task(db_session, task_data_generator):
#     """Фабрика для создания нескольких задач для пользователя"""
#
#     def _create_multiple_posts(count=3, assignee_id=None):
#         tasks = []
#
#         for _ in range(count):
#             task_data = task_data_generator(assignee_id=assignee_id)
#             task = Task(**task_data)
#             db_session.add(task)
#             tasks.append(task)
#
#         db_session.commit()
#
#         return tasks
#     return _create_multiple_posts