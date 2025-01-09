from typing import List
from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import comments as comments_repo
from src.repository.posts import PostRepository
from src.schemas.comments import CommentOut, CommentCreate, CommentUpdate
from src.entity.models import User, RoleEnum
from src.services.utils import get_current_user

router = APIRouter()

@router.post("/{post_id}", response_model=CommentOut)
async def create_comment(
    post_id: int,
    content: str = Form(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Creates a new comment on a post.

    Args:
        post_id (int): The ID of the post to comment on.
        content (str): The content of the comment.
        current_user (User, optional): The currently authenticated user. Defaults to dependency injection of get_current_user.
        db (AsyncSession, optional): The database session for executing queries. Defaults to dependency injection of get_db.

    Returns:
        CommentOut: The newly created comment.

    Raises:
        HTTPException: If an error occurs while creating the comment.
    """
    try:
        post = await PostRepository.get_post(db, post_id)
        db_comment = await comments_repo.create_comment(
            db,
            CommentCreate(content=content),
            user_id=current_user.id,
            post_id=post_id
        )
        return db_comment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{post_id}/comments", response_model=List[CommentOut])
async def get_comments_for_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves all comments for a specific post.

    Args:
        post_id (int): The ID of the post to retrieve comments for.
        db (AsyncSession, optional): The database session for executing queries. Defaults to dependency injection of get_db.

    Returns:
        List[CommentOut]: A list of comments for the specified post.

    Raises:
        HTTPException: If the post is not found.
    """
    post = await PostRepository.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comments = await comments_repo.get_comments_by_post(db, post_id)
    return comments

@router.put("/{comment_id}", response_model=CommentOut)
async def update_comment(
    comment_id: int,
    data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Updates a specific comment.

    Args:
        comment_id (int): The ID of the comment to update.
        data (CommentUpdate): The new data for the comment.
        current_user (User, optional): The currently authenticated user. Defaults to dependency injection of get_current_user.
        db (AsyncSession, optional): The database session for executing queries. Defaults to dependency injection of get_db.

    Returns:
        CommentOut: The updated comment.

    Raises:
        HTTPException: If the comment is not found or the user is not authorized to update the comment.
    """
    comment = await comments_repo.get_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")
    updated_comment = await comments_repo.update_comment(
        db=db,
        comment_id=comment_id,
        content=data.content,
        user_id=current_user.id
    )
    return updated_comment

@router.delete("/{comment_id}", response_model=dict)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Deletes a specific comment.

    Args:
        comment_id (int): The ID of the comment to delete.
        current_user (User, optional): The currently authenticated user. Defaults to dependency injection of get_current_user.
        db (AsyncSession, optional): The database session for executing queries. Defaults to dependency injection of get_db.

    Returns:
        dict: A message indicating successful deletion of the comment.

    Raises:
        HTTPException: If the comment is not found or the user is not authorized to delete the comment.
    """
    if current_user.role not in [RoleEnum.admin, RoleEnum.moderator]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    comment = await comments_repo.get_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    await comments_repo.delete_comment(
        db=db,
        comment_id=comment_id
    )
    return {"message": "Comment deleted successfully"}