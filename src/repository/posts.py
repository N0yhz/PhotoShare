from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from .base import BaseRepository
from src.entity.models import Post, Tag


class PostRepository(BaseRepository[Post]):
    def __init__(self, session: AsyncSession):
        super().__init__(Post, session)

    async def get_with_tags(self, post_id: int) -> Optional[Post]:
        result = await self.session.execute(
            select(Post)
            .options(selectinload(Post.tags))
            .where(Post.id == post_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int, limit: int = 10, offset: int = 0) -> List[Post]:
        result = await self.session.execute(
            select(Post)
            .options(selectinload(Post.tags))
            .where(Post.user_id == user_id)
        )
        return result.scalars().all()
    
    async def add_tags(self, post: Post, tag_names: List[str]):
        # Get or create tags
        for name in tag_names:
            result = await self.session.execute(
                select(Tag)
                .where(Tag.name == name)
            )   
            tag = result.scalar_one_or_none()

            if not tag:
                tag = Tag(name=name)
                self.session.add(tag)
            post.tags.append(tag)

        await self.session.commit()