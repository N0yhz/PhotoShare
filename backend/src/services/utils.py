from datetime import datetime, timedelta, timezone
import os

from dotenv import load_dotenv

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import TokenBlacklist, User, RoleEnum
from src.schemas.auth import TokenData
from src.repository.auth import RoleRepository
from src.conf.config import config


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
VERIFICATION_TOKEN_EXPIRE_HOURS = 24

oauth2_schema = OAuth2PasswordBearer(tokenUrl="api/auth/token")

async def get_user(db: AsyncSession, email: str):
    """
    Retrieves a user by their email address from the database.

    Args:
        db (AsyncSession): The database session.
        email (str): The email address of the user.

    Returns:
        User: The user object if found, otherwise None.
    """
    result = await db.execute(select(User).filter(User.email == email)) 
    return result.scalars().first()

async def create_verification_token(email: str) -> str:
    """
    Creates a verification token for email verification.

    Args:
        email (str): The email address to encode in the token.

    Returns:
        str: The encoded JWT token.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        hours=VERIFICATION_TOKEN_EXPIRE_HOURS
    )
    to_encode = {"exp": expire, "sub": email}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def decode_verification_token(token: str) -> str | None:
    """
    Decodes a verification token to retrieve the associated email.

    Args:
        token (str): The JWT token.

    Returns:
        str | None: The email if decoding is successful, otherwise None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None


async def create_access_token(data: dict):
    """
    Creates an access token with a limited expiration time.

    Args:
        data (dict): The data to encode in the token.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def create_refresh_token(data: dict):
    """
    Creates a refresh token with a longer expiration time.

    Args:
        data (dict): The data to encode in the token.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def decode_access_token(token: str) -> TokenData | None:
    """
    Decodes an access token to retrieve associated data.

    Args:
        token (str): The JWT token.

    Returns:
        TokenData | None: Token data if decoding is successful, otherwise None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return TokenData(email=email)
    except JWTError:
        return None


async def get_current_user(token: str = Depends(oauth2_schema), db: AsyncSession = Depends(get_db)):
    """
    Retrieves the current authenticated user based on the token.

    Args:
        token (str): The JWT token from the request.
        db (AsyncSession): The database session.

    Returns:
        User: The authenticated user.

    Raises:
        HTTPException: If the token is invalid or the user is banned.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = await get_user(db, email=token_data.email)

    if user.banned:
        raise HTTPException(status_code=403, detail="Your account is banned")
    return user


async def get_current_admin(user: User = Depends(get_current_user)):
    """
    Ensures the current user is an admin.

    Args:
        user (User): The current authenticated user.

    Returns:
        User: The admin user.

    Raises:
        HTTPException: If the user is not an admin.
    """
    if user.role.name == RoleEnum.admin.value:
        return user
    raise HTTPException(status_code=403, detail="Only admins can perform this action")
    
    
async def is_mod_or_admin(db: AsyncSession, user_id: int):
    """
    Checks if a user has moderator or admin privileges.

    Args:
        db (AsyncSession): The database session.
        user_id (int): The ID of the user.

    Returns:
        bool: True if the user is a moderator or admin, otherwise False.
    """
    user = RoleRepository.get_role_by_id(db, user_id)
    if user.role.name in [RoleEnum.admin.value, RoleEnum.moderator.value]:
        return True
    return False


class RoleChecker:
    """
    Dependency for checking if the user has one of the allowed roles.

    Args:
        allowed_roles (list[RoleEnum]): A list of allowed roles.

    Methods:
        __call__: Verifies the user's role and returns the user if allowed.
    """
    def __init__(self, allowed_roles: list[RoleEnum]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self, token: str = Depends(oauth2_schema), db: AsyncSession = Depends(get_db)
    ) -> User:
        """
        Verifies if the user has one of the allowed roles.

        Args:
            token (str): The JWT token from the request.
            db (AsyncSession): The database session.

        Returns:
            User: The user with an allowed role.

        Raises:
            HTTPException: If the user does not have the required role.
        """
        user = await get_current_user(token, db)

        if user.role.name not in [role.value for role in self.allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return user