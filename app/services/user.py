import logging
from typing import List, Optional

from sqlalchemy import delete, select, func

from app.db.models import User, UserRoles
from app.schemes.user import CreateUser, UserFilter
from app.security.auth import auth_service
from app.security.errors import AuthorizationError
from app.services.main_service import MainService

logger = logging.getLogger(__name__)


class UserService(MainService):
    async def create_user(self, input: CreateUser) -> User:
        session = self._get_async_session()
        hashed_password = auth_service.get_password_hash(input.password)
        raw_user = input.model_dump()
        raw_user.update({"password": hashed_password})
        user = User(**raw_user)
        email = input.email

        async with session() as db_session:
            result = await db_session.execute(
                select(User).filter_by(email=email)
            )

            old_user = result.scalars().one_or_none()

            if old_user:
                logger.error(
                    f"Пользователь с {email=} уже был создан."
                )
                raise ValueError(f"Пользователь с {email=} уже был создан.")

            db_session.add(user)
            await db_session.commit()

            logger.info(
                f"Пользователь c параметрами: {user=} успешно создан."
            )

            return user

    async def get_user_by_id(self, id: int) -> Optional[User]:
        session = self._get_async_session()

        async with session() as db_session:
            result = await db_session.execute(
                select(User).filter_by(id=id)
            )

            return result.scalars().first()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        session = self._get_async_session()

        async with session() as db_session:
            result = await db_session.execute(
                select(User).filter_by(email=email)
            )

            return result.scalars().first()

    async def delete_user(self, id: int, current_user: User) -> None:
        session = self._get_async_session()

        if (
            current_user.role == UserRoles.USER and id == current_user.id
        ) or (current_user.role == UserRoles.ADMIN):
            async with session() as db_session:
                result = await db_session.execute(
                    delete(User).filter_by(id=id)
                )

                await db_session.commit()

                if result.rowcount > 0:
                    logger.info(f"Пользователь c {id=} успешно удален.")
                else:
                    logger.error(f"Пользователь c {id=} не найден.")
                    raise ValueError(f"Пользователь c {id=} не найден.")
        else:
            raise AuthorizationError(
                f"Запись пользователя c {id=} принадлежит другому пользователю и не может быть удалена."
            )

    async def update_user(
        self, id: int, current_user: User, **kwargs
    ) -> User:
        session = self._get_async_session()

        if (
            current_user.role == UserRoles.USER and id == current_user.id
        ) or (current_user.role == UserRoles.ADMIN):
            async with session() as db_session:
                result = await db_session.execute(
                    select(User).filter_by(id=id)
                )
                user = result.scalars().one_or_none()

                if user is None:
                    logger.error(f"Пользователь c {id=} не найден.")
                    raise ValueError(f"Пользователь c {id=} не найден.")

                for key, value in kwargs.items():
                    if key == 'password':
                        value = auth_service.get_password_hash(
                            value
                        ) if value else value

                    if value:
                        setattr(user, key, value)

                await db_session.commit()

                logger.info(f"Пользователь c {id=} успешно обновлен.")

                return user
        else:
            raise AuthorizationError(
                f"Запись пользователя c {id=} принадлежит другому пользователю и не может быть обновлена."
            )

    async def get_users(self, skip: int, limit: int, sort_by: str, ascending: bool, filter: UserFilter) -> List[User]:
        session = self._get_async_session()
        query = select(User)

        if filter.email:
            query = query.where(User.email.contains(filter.email))

        if filter.first_name:
            query = query.where(User.first_name.contains(filter.first_name))

        if filter.last_name:
            query = query.where(User.last_name.contains(filter.last_name))

        if filter.created_at:
            query = query.where(func.date(User.created_at) == filter.created_at)

        async with session() as db_session:
            field = getattr(User, sort_by, None)

            if field is None:
                logger.error(f"У пользователя нет поля '{sort_by}'.")
                raise AttributeError(f"У пользователя нет поля '{sort_by}'.")

            if ascending:
                query = query.order_by(field)
            else:
                query = query.order_by(field).desc()

            result = await db_session.execute(query.offset(skip).limit(limit))

            return result.scalars().all()


user_service = UserService()
