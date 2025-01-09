from typing import List
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Comment, Post
from src.schemas.comments import CommentCreate
from src.services.utils import is_mod_or_admin

async def create_comment(
        db: AsyncSession,
        comment: CommentCreate,
        user_id: int,
        post_id: int
    ):
    """
    Creates a new comment in the database.

    Args:
        db (AsyncSession): The database session for executing queries.
        comment (CommentCreate): The comment creation data.
        user_id (int): The ID of the user creating the comment.
        post_id (int): The ID of the post to which the comment belongs.

    Returns:
        Comment: The newly created comment.
    """
    db_comment = Comment(
        user_id=user_id,
        post_id=post_id,
        content=comment.content
    )
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment

async def get_comments_by_post(db: AsyncSession, post_id: int) -> List[Comment]:
    """
    Retrieves comments for a specific post from the database.

    Args:
        db (AsyncSession): The database session for executing queries.
        post_id (int): The ID of the post for which to retrieve comments.

    Returns:
        List[Comment]: A list of comments for the specified post.
    """
    comments = await db.execute(
        select(Comment)
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at.desc())
    )
    comments = comments.scalars().all()
    return comments

async def get_comment(db: AsyncSession, comment_id: int) -> Comment | None:
    """
    Retrieves a specific comment from the database by its ID.

    Args:
        db (AsyncSession): The database session for executing queries.
        comment_id (int): The ID of the comment to retrieve.

    Returns:
        Comment | None: The comment object if found, otherwise None.
    """
    stmt = select(Comment).where(Comment.id == comment_id).options(selectinload(Comment.user))
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    return comment

async def update_comment(
    db: AsyncSession,
    comment_id: int,
    content: str,
    user_id: int
) -> Comment:
    """
    Updates the content of a specific comment.

    Args:
        db (AsyncSession): The database session for executing queries.
        comment_id (int): The ID of the comment to update.
        content (str): The new content for the comment.
        user_id (int): The ID of the user updating the comment.

    Returns:
        Comment: The updated comment object.

    Raises:
        HTTPException: If the comment is not found or if the user is not authorized to update it.
    """
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")
    comment.content = content
    comment.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(comment)
    return comment

async def delete_comment(
    db: AsyncSession,
    comment_id: int,
    user_id: int
):
    """
    Deletes a specific comment from the database.

    Args:
        db (AsyncSession): The database session for executing queries.
        comment_id (int): The ID of the comment to delete.
        user_id (int): The ID of the user requesting the deletion.

    Returns:
        dict: A message indicating the result of the deletion.

    Raises:
        HTTPException: If the comment is not found or if the user is not authorized to delete it.
    """
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != user_id and not await is_mod_or_admin(db, user_id):
        raise HTTPException(status_code=403, detail="Not authorized")
    await db.delete(comment)
    await db.commit()
    return {"message": "Comment deleted successfully"}