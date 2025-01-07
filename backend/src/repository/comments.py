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
        comments = await db.execute(
            select(Comment)
            .where(Comment.post_id == post_id)
            .order_by(Comment.created_at.desc())
        )
        comments = comments.scalars().all()
        return comments

async def get_comment(db: AsyncSession, comment_id: int) -> Comment | None:
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
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != user_id and not await is_mod_or_admin(db, user_id):
        raise HTTPException(status_code=403, detail="Not authorized")
    await db.delete(comment)
    await db.commit()
    return {"message": "Comment deleted successfully"}