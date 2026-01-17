import logging
from typing import List, Optional

from sqlalchemy import delete, select

from app.db.models import Task
from app.schemes.task import CreateTask
from app.services.main_service import MainService

logger = logging.getLogger(__name__)


class TaskService(MainService):
    async def create_task(self, input: CreateTask) -> Task:
        session = self._get_async_session()
        raw_task = input.model_dump()
        task = Task(**raw_task)

        async with session() as db_session:
            db_session.add(task)
            await db_session.commit()

            logger.info(
                f"Задача c параметрами: {task=} успешно создана."
            )

            return task

    async def get_task(self, id: int) -> Optional[Task]:
        session = self._get_async_session()

        async with session() as db_session:
            result = await db_session.execute(
                select(Task).filter_by(id=id)
            )

            return result.scalars().first()

    async def delete_task(self, id: int) -> None:
        session = self._get_async_session()

        async with session() as db_session:
            result = await db_session.execute(
                delete(Task).filter_by(id=id)
            )

            await db_session.commit()

            if result.rowcount > 0:
                logger.info(f"Задача c {id=} успешно удалена.")
            else:
                logger.error(f"Задача c {id=} не найдена.")
                raise ValueError(f"Задача c {id=} не найдена.")

    async def update_task(
        self, id: int, **kwargs
    ) -> Task:
        session = self._get_async_session()

        async with session() as db_session:
            result = await db_session.execute(
                select(Task).filter_by(id=id)
            )
            task = result.scalars().one_or_none()

            if task is None:
                logger.error(f"Задача c {id=} не найдена.")
                raise ValueError(f"Задача c {id=} не найдена.")

            for key, value in kwargs.items():
                if value:
                    setattr(task, key, value)

            await db_session.commit()

            logger.info(f"Задача c {id=} успешно обновлена.")

            return task

    async def get_tasks(self, skip: int, limit: int, sort_by: str, ascending: bool) -> List[Task]:
        session = self._get_async_session()

        async with session() as db_session:
            if ascending:
                query = select(Task).order_by(getattr(Task, sort_by))
            else:
                query = select(Task).order_by(getattr(Task, sort_by).desc())

            result = await db_session.execute(query.offset(skip).limit(limit))

            return result.scalars().all()


task_service = TaskService()
