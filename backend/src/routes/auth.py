from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.utils import oauth2_schema

from src.entity.models import RoleEnum, TokenBlacklist, User
from src.services.pass_utils import verify_password
from src.schemas.auth import UserCreate, UserResponse, Token
from src.repository.auth import RoleRepository, UserRepository
from src.database.db import get_db
from src.services.utils import RoleChecker, create_access_token, create_refresh_token, decode_access_token, get_current_user, get_current_admin
from src.services.cloudinary import CloudinaryService


router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    user_create: UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    user = await UserRepository.get_user_by_email(user_create.email, db)
    
    if user:
        raise HTTPException(status_code=409, detail="User already registered")
   
    user = await UserRepository.create_user(user_create, db)
    return user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await UserRepository.get_user_by_email(form_data.username, db)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = await create_access_token(data={"sub": user.email})
    refresh_token = await create_refresh_token(data={"sub": user.email})
    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_tokens(refresh_token: str, db: AsyncSession = Depends(get_db)):
    token_data = decode_access_token(refresh_token)
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(token_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = await create_access_token(data={"sub": user.email})
    refresh_token = await create_refresh_token(data={"sub": user.email})
    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )
    

@router.post("/update-avatar", response_model=UserResponse)
async def update_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        avatar = await CloudinaryService.upload_image(file)
        updated_user = await UserRepository.update_user_avatar(db, current_user.id, avatar)
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading avatar: {str(e)}")

@router.post("/update-profile", response_model=UserResponse)
async def update_profile(
    username: str = None,
    first_name: str = None,
    last_name: str = None,
    bio: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        updated_user = await UserRepository.update_user_profile(
            db, current_user.id, username, first_name, last_name, bio
        )
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")

@router.get("/my_info")
async def get_my_data(user: UserResponse = Depends(get_current_user)):
    return {"role": user.role.name, "username": user.username, "email": user.email}

@router.get("/users/{username}")
async def get_user_profile(user: UserResponse = Depends(UserRepository.get_user_by_username)):
    return {
        "username": user.username,
        "email": user.email,
        "role": user.role.name,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "bio": user.bio,
        "avatar": user.avatar,
    }


@router.post("/change_role")
async def change_role(
    username: str, 
    role_id: int,
    db: AsyncSession = Depends(get_db), 
    user: User = Depends(RoleChecker([RoleEnum.admin])),
):
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)
    
    target_user = await user_repo.get_user_by_username(username)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    target_role = await role_repo.get_role_by_id(role_id)
    if not target_user:
        raise HTTPException(status_code=400, detail="Invalid role ID")
    
    return await user_repo.change_user_role(target_user, target_role)

@router.get("/current-admin")
async def get_current_admin(user: User = Depends(get_current_admin)):
    return user

@router.post("/ban/{user_id}")
async def ban_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    async with session.begin():
        # Get the user to ban
        user_to_ban = await session.get(User, user_id)
        if not user_to_ban:
            raise HTTPException(status_code=404, detail="User not found")
        if user_to_ban.id == current_admin.id:
            raise HTTPException(status_code=400, detail="Cannot ban yourself")
        if user_to_ban.banned:
            raise HTTPException(status_code=400, detail="User is already banned")
        
        # Set banned to True
        user_to_ban.banned = True
        await session.commit()
    
    return {"message": f"User {user_to_ban.id} has been banned."}

@router.post("/unban/{user_id}")
async def unban_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    async with session.begin():
        # Get the user to unban
        user_to_unban = await session.get(User, user_id)
        if not user_to_unban:
            raise HTTPException(status_code=404, detail="User not found")
        if user_to_unban.id == current_admin.id:
            raise HTTPException(status_code=400, detail="Cannot unban yourself")
        if not user_to_unban.banned:
            raise HTTPException(status_code=400, detail="User is not banned")
        
        # Set banned to False
        user_to_unban.banned = False
        await session.commit()
    
    return {"message": f"User {user_to_unban.id} has been unbanned."}


@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_schema), 
    db: AsyncSession = Depends(get_db)
):
    # Validate the token
    token_data = await decode_access_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Check if the token is already blacklisted
    query = select(TokenBlacklist).where(TokenBlacklist.token == token)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Token is already blacklisted")
    
    # Add the token to the blacklist
    blacklisted_token = TokenBlacklist(token=token)
    db.add(blacklisted_token)
    await db.commit()
    
    return {"message": "Successfully logged out"}
