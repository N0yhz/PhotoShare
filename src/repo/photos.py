from typing import List

from sqlalchemy.orm import Session
from src.entity.models import Post
from src.schemas.photos import CreatePost


async def get_post(post_id: int, user_id: int, db: Session) -> Post:

    post = db.query(Post).filter(Post.id == post_id, Post.user_id == user_id).first()
    return post


async def update_post(post_id: int, user_id: int, body: Post, db: Session) -> Post | None:

    post: object = db.query(Post).filter(Post.id == post_id, Post.user_id == user_id).first()
    if post:
        post.cloudinary_url = body.cloudinary_url
        post.description = body.description
        db.commit()
    return post


async def remove_post(post_id: int, user_id: int, db: Session) -> Post | None:

    post = db.query(Post).filter(Post.id == post_id, Post.user_id == user_id).first()
    if post:
        db.delete(post)
        db.commit()
    return post


async def get_posts(user_id: int, db: Session) -> List[Post]:

    posts = db.query(Post).filter(Post.user_id == user_id).all()
    return posts


async def create_post(body: CreatePost, user_id: int, db: Session):

    post = Post(cloudinary_url=body.cloudinary_url, description=body.description, user_id=user_id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post
