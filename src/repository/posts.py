from typing import List
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Post, Tag, Transformation
from src.schemas.posts import PostCreate

class PostRepository():
    @staticmethod
    async def create_post(db: AsyncSession, post: PostCreate, user_id: int):
        db_post = Post(
            cloudinary_url=post.cloudinary_url,
            description=post.description,
            user_id=user_id)
        db.add(db_post)
        await db.commit()
        await db.refresh(db_post)
        return db_post

    @staticmethod
    async def get_post(db: AsyncSession, post_id: int) -> Post | None:
        stmt = select(Post).where(Post.id == post_id).options(selectinload(Post.user))
        result = await db.execute(stmt)
        post = result.scalar_one_or_none()
        return post

    @staticmethod
    async def get_with_tags(db: AsyncSession, post_id: int) -> Post:
        stmt = select(Post).where(Post.id == post_id).options(selectinload(Post.tags))
        result = await db.execute(stmt)
        post = result.scalar_one_or_none()
        return post

    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: int) -> List[Post]:
        result = await db.execute(
            select(Post)
            .options(selectinload(Post.tags))
            .where(Post.user_id == user_id)
        )
        return result.scalars().all()

    @staticmethod
    async def update_post(db: AsyncSession, post_id: int, description: str):
            db_post = await db.get(Post, post_id)
            if not db_post:
                print(f"Post with ID {post_id} not found.")
                return None
            
            db_post.description = description
            db_post.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(db_post)
            return db_post

    @staticmethod
    async def delete_post(db: AsyncSession, post_id: int) -> Post | None:
        post = await PostRepository.get_post(db, post_id)
        if post:
            await db.delete(post)
            await db.commit()
            return post
        return None


    @staticmethod
    async def add_tags_to_post(
        db: AsyncSession,
        post_id: int,
        tag_names: List[str]
    ) -> Post:
        async with db.begin():
            post = await db.get(Post, post_id)
            if not post:
                raise HTTPException(status_code=404, detail="Post not found")
            
            for tag_name in tag_names:
                tag = await db.execute(select(Tag).where(Tag.name == tag_name))
                tag = tag.scalar_one_or_none()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                if tag not in post.tags:
                    post.tags.append(tag)
            
            await db.refresh(post)
            return post
        