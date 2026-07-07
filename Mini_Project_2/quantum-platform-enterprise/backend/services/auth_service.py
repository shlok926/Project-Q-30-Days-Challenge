from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import UserCreate
from models.user import User
from repositories.user_repo import user_repo
from core.security.password import get_password_hash, verify_password
from core.exceptions.base import ConflictError
import uuid

async def register_user(db: AsyncSession, user_in: UserCreate) -> User:
    existing = await user_repo.get_by_email(db, user_in.email)
    if existing:
        raise ConflictError("User with this email already exists")
    
    user_data = user_in.model_dump()
    user_data["password_hash"] = get_password_hash(user_data.pop("password"))
    
    user = await user_repo.create(db, obj_in=user_data)
    return user

async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    user = await user_repo.get_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
