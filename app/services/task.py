import logging
from typing import List, Optional

from sqlalchemy import delete, select

from app.db.models import Task, User, UserRoles
from app.schemes.task import CreateTask
from app.security.errors import AuthorizationError
from app.services.main_service import MainService
from app.services.mappings import TASK_STATUSES_MAPPING

logger = logging.getLogger(__name__)


class TaskService(MainService):
    async def create_task(self, current_user: User, input: CreateTask) -> Task:
        session = self._get_async_session()
        raw_task = input.model_dump()
        task = Task(**raw_task)

        task.assignee_id = current_user.id

        async with session() as db_session:
            db_session.add(task)
            await db_session.commit()

            logger.info(
                f"Задача c параметрами: {task=} успешно создана."
            )

            return task

    async def get_task(self, current_user: User, id: int) -> Optional[Task]:
        session = self._get_async_session()

        async with session() as db_session:
            result = await db_session.execute(
                select(Task).filter_by(id=id)
            )

            task = result.scalars().first()

            if task:
                if current_user.role == UserRoles.USER and task.assignee_id == current_user.id:
                    return task
                elif current_user.role == UserRoles.ADMIN:
                    return task
                else:
                    raise AuthorizationError(f"Задача c {id=} принадлежит другому пользователю и не может быть просмотрена.")

            return None

    async def delete_task(self, id: int, current_user, User) -> None:
        session = self._get_async_session()

        async with session() as db_session:
            result = await db_session.execute(
                select(Task).filter_by(id=id)
            )

            task = result.scalars().first()

            if (
                current_user.role == UserRoles.USER and task.assignee_id == current_user.id
            ) or (current_user.role == UserRoles.ADMIN):
                result = await db_session.execute(
                    delete(Task).filter_by(id=id)
                )

                await db_session.commit()

                if result.rowcount > 0:
                    logger.info(f"Задача c {id=} успешно удалена.")
                else:
                    logger.error(f"Задача c {id=} не найдена.")
                    raise ValueError(f"Задача c {id=} не найдена.")
            else:
                raise AuthorizationError(
                    f"Задача c {id=} принадлежит другому пользователю и не может быть удалена."
                )

    async def update_task(
        self, id: int, current_user: User, **kwargs
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

            if (
                current_user.role == UserRoles.USER and task.assignee_id == current_user.id
            ) or (current_user.role == UserRoles.ADMIN):
                for key, value in kwargs.items():
                    if key == 'status':
                        if not self.is_valid_new_task_status(
                            task.status, value
                        ):
                            raise ValueError(
                                f"Задача не может сменить статус с {task.status} на {value}. "
                                f"Доступные варианты: {TASK_STATUSES_MAPPING[task.status]}"
                            )

                    if value:
                        setattr(task, key, value)

                await db_session.commit()

                logger.info(f"Задача c {id=} успешно обновлена.")

                return task
            else:
                raise AuthorizationError(
                    f"Задача c {id=} принадлежит другому пользователю и не может быть обновлена."
                )

    async def get_tasks(self, skip: int, limit: int, sort_by: str, ascending: bool, current_user: User) -> List[Task]:
        session = self._get_async_session()

        async with session() as db_session:
            if current_user.role == UserRoles.USER:
                query = select(Task).filter_by(assignee_id=current_user.id)
            else:
                query = select(Task)

            field = getattr(Task, sort_by, None)

            if field is None:
                logger.error(f"У задачи нет поля '{sort_by}'.")
                raise AttributeError(f"У задачи нет поля '{sort_by}'.")

            if ascending:
                query = query.order_by(field)
            else:
                query = query.order_by(field).desc()

            result = await db_session.execute(query.offset(skip).limit(limit))

            return result.scalars().all()

    def is_valid_new_task_status(self, current_status: str, new_status: str) -> bool:
        return new_status in TASK_STATUSES_MAPPING[current_status]


task_service = TaskService()
