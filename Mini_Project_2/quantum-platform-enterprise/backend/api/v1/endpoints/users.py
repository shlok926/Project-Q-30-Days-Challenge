from fastapi import APIRouter, Depends
from models.user import User
from schemas.user import UserResponse
from api.deps import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user
