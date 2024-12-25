from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository.comments import CommentRepository
from src.schemas.comments import CommentBase, CommentCreate, CommentUpdate
from src.entity.models import User, Comment
from src.services.utils import get_current_user

router = APIRouter()

@router.post("/", response_model=CommentBase)
async def create_comment(
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    comment_repo = CommentRepository(db)
    return await comment_repo.create(
        **comment_data.dict(),
        user_id=current_user.id
    )

@router.get("/post/{post_id}", response_model=List[CommentBase])
async def get_post_comments(
    post_id: int,
    db: AsyncSession = Depends(get_db)
):
    comment_repo = CommentRepository(db)
    return await comment_repo.get_by_post(post_id)

@router.put("/{comment_id}", response_model=List[CommentBase])
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    comment_repo = CommentRepository(db)
    comment = await comment_repo.get(comment_id)

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to update this comment")
    
    return await comment_repo.update(comment_id, **comment_data.dict())