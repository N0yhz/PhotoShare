from typing import Optional
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.auth import UserCreate
from src.entity.models import User, RoleEnum, Role
from src.services.pass_utils import get_password_hash
from src.database.db import get_db

class UserRepository:
    async def create_user(user_create: UserCreate, db: AsyncSession):
        hashed_password = get_password_hash(user_create.password)
        
        existing_users = await db.execute(select(User).limit(1))
        users_exist = existing_users.scalars().first() is not None
        
        if not users_exist:
            user_role = await RoleRepository(db).get_role_by_name(RoleEnum.admin)
        else:
            user_role = await RoleRepository(db).get_role_by_name(RoleEnum.user)
        
        new_user = User(
            username=user_create.username, 
            email=user_create.email, 
            hashed_password=hashed_password, 
            role_id = user_role.id, 
            is_verified=False
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    
    async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
        query = select(User).filter_by(email = email)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)) -> Optional[User]:
        query = select(User).where(User.username == username)
        result = await db.execute(query)
        user = result.scalars().first()
        return user
        
    async def activate_user(self, user: User):
        user.is_active = True
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        
    async def change_user_role(self, user: User, role: Role):
        user.role_id = role.id
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        
        # user.role_id = role.id
        # await db.commit()
        
        return {"message": f"Role of {user.username} changed successfully to {user.role.name}"}
    
    async def update_user_avatar(db: AsyncSession, user_id: int, avatar: str):
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
        query = select(Role).where(Role.name == name.value)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_role_by_id(self, role_id):
        query = select(Role).where(Role.id == role_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()