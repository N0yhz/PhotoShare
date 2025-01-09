from typing import List
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Post, Tag
from src.schemas.posts import PostCreate


class PostRepository():
    """
    Repository class for managing post-related database operations.
    """
    @staticmethod
    async def create_post(db: AsyncSession, post: PostCreate, user_id: int):
        """
        Creates a new post in the database.

        Args:
            db (AsyncSession): The database session for executing queries.
            post (PostCreate): The post creation data.
            user_id (int): The ID of the user creating the post.

        Returns:
            Post: The newly created post.
        """
        db_post = Post(
            cloudinary_url=post.cloudinary_url,
            description=post.description,
            user_id=user_id)
        db.add(db_post)
        await db.commit()
        await db.refresh(db_post)
        return db_post

    @staticmethod
    async def get_all_posts(db: AsyncSession) -> List[Post]:
        """
        Retrieves all posts from the database.

        Args:
            db (AsyncSession): The database session for executing queries.

        Returns:
            List[Post]: A list of all posts.
        """
        result = await db.execute(select(Post).options(selectinload(Post.tags)))
        return result.scalars().all()

    @staticmethod
    async def get_post(db: AsyncSession, post_id: int) -> Post | None:
        """
        Retrieves a specific post from the database by its ID.

        Args:
            db (AsyncSession): The database session for executing queries.
            post_id (int): The ID of the post to retrieve.

        Returns:
            Post | None: The post object if found, otherwise None.
        """
        stmt = select(Post).where(Post.id == post_id).options(selectinload(Post.user))
        result = await db.execute(stmt)
        post = result.scalar_one_or_none()
        return post

    @staticmethod
    async def get_with_tags(db: AsyncSession, post_id: int) -> Post:
        """
        Retrieves a specific post from the database by its ID, including its tags.

        Args:
            db (AsyncSession): The database session for executing queries.
            post_id (int): The ID of the post to retrieve.

        Returns:
            Post: The post object if found, otherwise None.
        """
        stmt = select(Post).where(Post.id == post_id).options(selectinload(Post.tags))
        result = await db.execute(stmt)
        post = result.scalar_one_or_none()
        return post

    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: int) -> List[Post]:
        """
        Retrieves posts from the database for a specific user by user ID.

        Args:
            db (AsyncSession): The database session for executing queries.
            user_id (int): The ID of the user whose posts are to be retrieved.

        Returns:
            List[Post]: A list of posts for the specified user.
        """
        result = await db.execute(
            select(Post)
            .options(selectinload(Post.tags))
            .where(Post.user_id == user_id)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_posts_by_tag(db: AsyncSession, tag_id: int) -> List[Post]:
        result = await db.execute(
            select(Post)
            .options(selectinload(Post.tags))
            .join(Post.tags)
            .where(Tag.id == tag_id)
        )
        return result.scalars().all()
    
    @staticmethod
    async def update_post(db: AsyncSession, post_id: int, description: str):
        """
        Updates the description of a specific post.

        Args:
            db (AsyncSession): The database session for executing queries.
            post_id (int): The ID of the post to update.
            description (str): The new description for the post.

        Returns:
            Post | None: The updated post object if found, otherwise None.
        """
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
        """
        Deletes a specific post from the database by its ID.

        Args:
            db (AsyncSession): The database session for executing queries.
            post_id (int): The ID of the post to delete.

        Returns:
            Post | None: The deleted post object if found, otherwise None.
        """
        post = await PostRepository.get_post(db, post_id)
        if post:
            await db.delete(post)
            await db.commit()
            return post
        return None

    @staticmethod
    async def add_tags_to_post(db: AsyncSession, post_id: int, tags: List[str]) -> Post:
        """
        Adds tags to a specific post.

        Args:
            db (AsyncSession): The database session for executing queries.
            post_id (int): The ID of the post to which tags will be added.
            tags (List[str]): The list of tags to add to the post.

        Returns:
            Post: The updated post object with the added tags.

        Raises:
            HTTPException: If the post is not found.
        """
        post = await db.get(Post, post_id)

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        for tag_data in tags:
            tag = await db.scalar(select(Tag).where(Tag.name == tag_data).limit(1))
            if not tag:
                tag = Tag(name=tag_data)
                db.add(tag)
                await db.commit()
                await db.refresh(tag)

            if tag not in post.tags:
                post.tags.append(tag)

        await db.commit()
        await db.refresh(post)
        return post
