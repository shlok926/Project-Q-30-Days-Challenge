from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from core.security.jwt import ALGORITHM
from core.config.settings import settings
from jose import jwt, JWTError
from models.user import User
from repositories.user_repo import user_repo
from core.exceptions.base import AuthenticationError, AuthorizationError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Token missing subject")
    except JWTError:
        raise AuthenticationError("Could not validate credentials")
    
    user = await user_repo.get(db, id=user_id)
    if not user:
        raise AuthenticationError("User not found")
    return user

def require_role(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role.value != required_role and current_user.role.value != "admin":
            raise AuthorizationError("Not enough permissions")
        return current_user
    return role_checker
