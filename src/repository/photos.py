from typing import List

from sqlalchemy.orm import Session
from src.entity.models import Post
from src.schemas.photos import CreatePost


async def get_post(post_id: int, user_id: int, db: Session) -> Post:
    """
    Retrieves a post from the database based on the given post ID and user ID.

    Args:
        post_id (int): The ID of the post to retrieve.
        user_id (int): The ID of the user, owner of the post.
        db (Session): The database session to execute the query.

    Returns:
        Post: The post that matches the given criteria, or None if no such post is found.
    """
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == user_id).first()
    return post


async def update_post(post_id: int, user_id: int, body: Post, db: Session) -> Post | None:
    """
    Updates a post in the database based on the given post ID and user ID.

    Args:
        post_id (int): The ID of the post to update.
        user_id (int): The ID of the user, owner of the post.
        body (Post): The updated post data.
        db (Session): The database session to execute the query.

    Returns:
        Post | None: The updated post if found, otherwise None.
    """
    post: object = db.query(Post).filter(Post.id == post_id, Post.user_id == user_id).first()
    if post:
        post.cloudinary_url = body.cloudinary_url
        post.description = body.description
        db.commit()
    return post


async def remove_post(post_id: int, user_id: int, db: Session) -> Post | None:
    """
    Removes a post from the database based on the given post ID and user ID.

    Args:
        post_id (int): The ID of the post to remove.
        user_id (int): The ID of the user, owner of the post.
        db (Session): The database session to execute the query.

    Returns:
        Post | None: The removed post if found, otherwise None.
    """
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == user_id).first()
    if post:
        db.delete(post)
        db.commit()
    return post


async def get_posts(user_id: int, db: Session) -> List[Post]:
    """
    Retrieves all posts from the database for a given user ID.

    Args:
        user_id (int): The ID of the user whose posts are to be retrieved.
        db (Session): The database session to execute the query.

    Returns:
        List[Post]: A list of posts for the given user.
    """
    posts = db.query(Post).filter(Post.user_id == user_id).all()
    return posts


async def create_post(body: CreatePost, user_id: int, db: Session):
    """
    Creates a new post in the database.

    Args:
        body (CreatePost): The data for the new post.
        user_id (int): The ID of the user creating the post.
        db (Session): The database session to execute the query.

    Returns:
        Post: The created post.
    """
    post = Post(cloudinary_url=body.cloudinary_url, description=body.description, user_id=user_id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

