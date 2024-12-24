from sqlalchemy import select

from src.schemas.auth import UserCreate
from src.entity.models import User, RoleEnum, Role
from src.services.pass_utils import get_password_hash



class UserRepository:
    def __init__(self, session):
        self.session = session

    async def create_user(self, user_create: UserCreate):
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
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username):
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
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