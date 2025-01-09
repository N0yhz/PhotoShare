from typing import Optional
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.auth import UserCreate
from src.entity.models import User, RoleEnum, Role
from src.services.pass_utils import get_password_hash
from src.database.db import get_db

class UserRepository:
    """
    Repository class for managing user-related database operations.
    """
    def __init__(self, session):
        self.session = session
    
    async def create_user(self, user_create: UserCreate):
        """
        Creates a new user in the database with a hashed password and assigns an appropriate role.

        Args:
            user_create (UserCreate): An object containing user creation data.
            db (AsyncSession): The database session for executing queries.

        Returns:
            User: The newly created user object.

        Raises:
            SQLAlchemyError: If there is an error committing the transaction to the database.
        """
        hashed_password = get_password_hash(user_create.password)

        existing_users = await self.session.execute(select(User).limit(1))
        users_exist = existing_users.scalars().first() is not None

        if not users_exist:
            user_role = await RoleRepository(self.session).get_role_by_name(RoleEnum.admin)
        else:
            user_role = await RoleRepository(self.session).get_role_by_name(RoleEnum.user)

        new_user = User(
            username=user_create.username, 
            email=user_create.email, 
            hashed_password=hashed_password, 
            role_id = user_role.id, 
            is_verified=False
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user
    
    async def get_user_by_email(self, email):
        """
        Retrieves a user from the database by email.

        Args:
            email (str): The email of the user to retrieve.
            db (AsyncSession, optional): The database session for executing queries. Defaults to dependency injection of get_db.

        Returns:
            User: The user object if found, otherwise None.

        Raises:
            SQLAlchemyError: If there is an error executing the query.
        """
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username) -> Optional[User]:
        """
        Retrieves a user from the database by username.

        Args:
            username (str): The username of the user to retrieve.
            db (AsyncSession, optional): The database session for executing queries. Defaults to dependency injection of get_db.

        Returns:
            Optional[User]: The user object if found, otherwise None.

        Raises:
            SQLAlchemyError: If there is an error executing the query.
        """
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
        
    async def get_all_users(self):
        result = await self.session.execute(select(User))
        return result.scalars().all()
    
    async def activate_user(self, user: User):
        """
        Activates a user's account.

        Args:
            user (User): The user object to activate.

        Returns:
            None

        Raises:
            SQLAlchemyError: If there is an error committing the transaction to the database.
        """
        
        user.is_active = True
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        
    async def change_user_role(db: AsyncSession, user: User, role: Role):
        """
        Changes the role of a user.

        Args:
            user (User): The user object whose role is to be changed.
            role (Role): The new role to assign to the user.

        Returns:
            dict: A message indicating the role change.

        Raises:
            SQLAlchemyError: If there is an error committing the transaction to the database.
        """
        user.role_id = role.id
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return {"message": f"Role of {user.username} changed successfully to {user.role.name}"}
    
    async def update_user_avatar(db: AsyncSession, user_id: int, avatar: str):
        """
        Updates the avatar of a user.

        Args:
            db (AsyncSession): The database session for executing queries.
            user_id (int): The ID of the user whose avatar is to be updated.
            avatar (str): The new avatar URL.

        Returns:
            User: The updated user object if found, otherwise None.

        Raises:
            SQLAlchemyError: If there is an error committing the transaction to the database.
        """
        query = select(User).filter_by(id=user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        if user:
            user.avatar = avatar
            await db.commit()
            await db.refresh(user)
        return user
    
    async def update_user_profile(
            db: AsyncSession, 
            user_id: int,
            username: Optional[str] = None,
            first_name: Optional[str] = None,
            last_name: Optional[str] = None, 
            bio: Optional[str] = None
        ):
        """
        Updates the profile of a user.

        Args:
            db (AsyncSession): The database session for executing queries.
            user_id (int): The ID of the user whose profile is to be updated.
            username (Optional[str], optional): The new username. Defaults to None.
            first_name (Optional[str], optional): The new first name. Defaults to None.
            last_name (Optional[str], optional): The new last name. Defaults to None.
            bio (Optional[str], optional): The new bio. Defaults to None.

        Returns:
            User: The updated user object if found, otherwise None.

        Raises:
            SQLAlchemyError: If there is an error committing the transaction to the database.
        """
        query = select(User).filter_by(id=user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            if username:
                user.username = username
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            if bio:
                user.bio = bio
        await db.commit()
        await db.refresh(user)
        return user
    
class RoleRepository:
    def __init__(self, session):
        self.session = session

    async def get_role_by_name(self, name: RoleEnum):
        """
        Retrieves a role from the database by its name.

        Args:
            name (RoleEnum): The name of the role to retrieve.

        Returns:
            Role: The role object if found, otherwise None.

        Raises:
            SQLAlchemyError: If there is an error executing the query.
        """
        query = select(Role).where(Role.name == name.value)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_role_by_id(self, role_id):
        """
        Retrieves a role from the database by its ID.

        Args: role_id (int): The ID of the role to retrieve.

        Returns:
            Role: The role object if found, otherwise None.

        Raises:
            SQLAlchemyError: If there is an error executing the query.
        """
        query = select(Role).where(Role.id == role_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
