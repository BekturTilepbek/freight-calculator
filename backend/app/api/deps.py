from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.crud import user as crud_user
from app.db.session import get_db
from app.models.user import User, UserRole

# tokenUrl — путь до эндпоинта логина (для Swagger-кнопки "Authorize")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Извлекает текущего пользователя из JWT-токена."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невалидный токен или сессия истекла",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = await crud_user.get(db, int(user_id))
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def require_role(*allowed: UserRole):
    """
    Фабрика зависимости для проверки роли.
    Использование: current_user: User = Depends(require_role(UserRole.ADMIN))
    """
    async def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для выполнения действия",
            )
        return current_user
    return checker