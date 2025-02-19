from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: EmailStr
    

class UserCreate(UserBase):
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    bio: Optional[str]

    model_config = ConfigDict(from_attributes = True)
        
        
class TokenData(BaseModel):
    email: str | None = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str