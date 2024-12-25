from typing import List
from sqlalchemy import select
from src.entity.models import Comment
from .base import BaseRepository

class CommentRepository(BaseRepository[Comment]):
    async def get_by_post(self, post_id: int) -> List[Comment]:
        result = await self.session.execute(
            select(Comment)
            .where(Comment.post_id == post_id)
            .order_by(Comment.created_at)
        )
        return result.scalars().all()
    
    async def get_by_user(self, user_id: int) -> List[Comment]:
        result = await self.session.execute(
            select(Comment)
            .where(Comment.user_id == user_id)
            .order_by(Comment.created_at)
        )
        return result.scalars().all()