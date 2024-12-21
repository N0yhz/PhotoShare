from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from jinja2 import Environment, FileSystemLoader

from src.schemas.auth import UserCreate, UserResponse
from src.repo.auth import UserRepository
from src.database.db import get_db


router = APIRouter()
env = Environment(loader=FileSystemLoader("src/services/templates"))


@router.post("/register", response_model=UserResponse)
async def register(
    user_create: UserCreate, 
    background_tasks: BackgroundTasks, 
    db: AsyncSession = Depends(get_db)
):
    
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(user_create.email)
    
    if user:
        raise HTTPException(status_code=409, detail="User already registered")
   
    user = await user_repo.create_user(user_create)
    
    return user

