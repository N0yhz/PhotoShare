from sqlalchemy import select

from src.schemas.auth import UserCreate
from src.entity.models import User, RoleEnum, Role
from src.services.pass_utils import get_password_hash


class UserRepository:
    def __init__(self, session):
        self.session = session

    async def create_user(self, user_create: UserCreate):
        hashed_password = get_password_hash(user_create.password)
        user_role = await RoleRepository(self.session).get_role_by_name(RoleEnum.user)
        
        new_user = User(
            username=user_create.username, 
            email=user_create.email, 
            hashed_password=hashed_password, 
            role_id = user_role.id, 
            is_active=False
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        
        return new_user
    

class RoleRepository:
    def __init__(self, session):
        self.session = session

    async def get_role_by_name(self, name: RoleEnum):
        query = select(Role).where(Role.name == name.value)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()