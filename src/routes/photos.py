from typing import List
from fastapi import APIRouter, status, Depends, HTTPException, Query
from fastapi_limiter.depends import RateLimiter

from src.schemas.photos import ResponsePost, CreatePost
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.repo import photos as repository_photos
from src.entity.models import User
from src.services.utils import get_current_user
from src.services.utils import RoleChecker
from src.entity.models import RoleEnum, User


router = APIRouter(prefix='/posts', tags=["posts"], dependencies=[Depends(get_current_user)])


@router.get('/{post_id}', response_model=ResponsePost, status_code=status.HTTP_200_OK)
async def get_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    user_id = current_user.id
    post = await repository_photos.get_post(post_id, user_id, db)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No posts')
    return contact


@router.get('/', response_model=List[ResponsePost], status_code=status.HTTP_200_OK)
async def get_posts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    posts = await repository_photos.get_posts(user_id, db)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No posts')
    return posts


@router.put("/{post_id}", response_model=ResponsePost)
async def update_post(body: CreatePost,
                      post_id: int,
                      current_user: User = Depends(get_current_user),
                      db: Session = Depends(get_db)
                      ):
    user_id = current_user.id
    post = await repository_photos.update_post(post_id, user_id, body, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.delete("/{contact_id}", response_model=ResponsePost)
async def remove_post(post_id: int,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    tag = await repository_photos.remove_post(post_id, user_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.post('/', response_model=ResponsePost, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_post(body: CreatePost,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    return await repository_photos.create_post(body, user_id, db)
=======

@router.get("/secret_for_all")
async def read_secret(
    user: User = Depends(RoleChecker([RoleEnum.user, RoleEnum.moderator, RoleEnum.admin])),
):
    return {"message": "Secret message for all authenticated users"}


@router.get("/secret_for_moderators")
async def read_secret(
    user: User = Depends(RoleChecker([RoleEnum.moderator, RoleEnum.admin])),
):
    return {"message": "Secret message for moderators"}


@router.get("/secret_for_admin")
async def read_secret(
    user: User = Depends(RoleChecker([RoleEnum.admin])),
):
    return {"message": "Secret message for admin"}
