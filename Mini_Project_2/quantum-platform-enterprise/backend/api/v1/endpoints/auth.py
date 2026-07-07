from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from schemas.user import UserCreate, UserResponse
from services.auth_service import register_user, authenticate_user
from fastapi.security import OAuth2PasswordRequestForm
from core.exceptions.base import AuthenticationError
from pydantic import BaseModel

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    return await register_user(db, user_in)

@router.post("/login", response_model=Token)
async def login(db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise AuthenticationError("Incorrect email or password")
    
    from core.security.jwt import create_access_token
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}
