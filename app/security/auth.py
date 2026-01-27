from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select

from app.db.models import User
from app.schemes.auth import TokenData
from app.services.main_service import MainService

# Настройки безопасности
SECRET_KEY = "мой_секретный_ключ_здесь"  # В продакшене используйте переменные окружения
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()

class AuthService(MainService):
    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt

    def verify_token(self, token: str, credentials_exception):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            role: str = payload.get("role")

            if email is None:
                raise credentials_exception

            token_data = TokenData(email=email, role=role)
        except JWTError:
            raise credentials_exception

        return token_data

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
    ):
        credentials_exception = HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Не удалось проверить учетные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )
        token = credentials.credentials
        token_data = self.verify_token(token, credentials_exception)

        session = self._get_async_session()

        async with session() as db_session:
            result = await db_session.execute(
                select(User).filter_by(email=token_data.email)
            )
            user = result.scalars().one_or_none()

            if user is None:
                raise credentials_exception

            return user

    async def get_current_active_user(self, current_user: User = Depends(get_current_user)):
        if not current_user.is_active:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Неактивный пользователь")

        return current_user

    async def check_required_role(self, current_user: User, allowed_roles: List[str] = []):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="У вас нет достаточных прав для доступа к этому ресурсу.",
            )


auth_service = AuthService()
