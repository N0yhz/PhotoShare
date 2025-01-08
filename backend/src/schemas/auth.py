from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional


class UserBase(BaseModel):
    """
    Base schema for user data.

    Attributes:
        username (str): The username of the user.
        email (EmailStr): The email address of the user.
        """
    username: str
    email: EmailStr
    

class UserCreate(UserBase):
    """
    Schema for creating a new user.

    Inherits:
        UserBase

    Attributes:
        password (str): The password for the new user.
    """
    password: str


class UserResponse(BaseModel):
    """
    Schema for user data returned in API responses.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        email (EmailStr): The email address of the user.
        avatar (Optional[str]): The URL of the user's avatar, if available.
        first_name (Optional[str]): The first name of the user, if available.
        last_name (Optional[str]): The last name of the user, if available.
        bio (Optional[str]): The biography of the user, if available.
    """
    id: int
    username: str
    email: EmailStr
    avatar: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    bio: Optional[str]

    model_config = ConfigDict(from_attributes = True)
        
        
class TokenData(BaseModel):
    """
    Schema for token data.

    Attributes:
        email (Optional[str]): The email address associated with the token.
    """
    email: str | None = None


class Token(BaseModel):
    """
    Schema for authentication tokens.

    Attributes:
        access_token (str): The access token for the user.
        refresh_token (str): The refresh token for the user.
        token_type (str): The type of the token (e.g., 'Bearer').
    """
    access_token: str
    refresh_token: str
    token_type: str