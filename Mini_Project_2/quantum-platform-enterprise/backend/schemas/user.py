from pydantic import BaseModel, EmailStr, ConfigDict
import uuid
from datetime import datetime
from typing import Optional
from models.user import RoleEnum

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: uuid.UUID
    role: RoleEnum
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
