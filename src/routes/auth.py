from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import RoleEnum, User
from src.services.pass_utils import verify_password
from src.schemas.auth import UserCreate, UserResponse, Token
from src.repo.auth import RoleRepository, UserRepository
from src.database.db import get_db
from src.services.utils import RoleChecker, create_access_token, create_refresh_token, decode_access_token, get_current_user


router = APIRouter()


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


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_tokens(refresh_token: str, db: AsyncSession = Depends(get_db)):
    token_data = decode_access_token(refresh_token)
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_username(token_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )
    

@router.get("/my_info")
async def get_my_data(user: UserResponse = Depends(get_current_user)):
    return {"role": user.role.name, "username": user.username, "email": user.email}


@router.post("/change_role")
async def change_role(
    username: str, role_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(RoleChecker([RoleEnum.admin])),
):
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)
    
    target_user = await user_repo.get_user_by_username(username)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    role = await role_repo.get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=400, detail="Invalid role ID")
    
    target_user.role_id = role.id
    await db.commit()

    return {"message": f"Role of user {target_user.username} changed successfully to {role.name}"}
    


