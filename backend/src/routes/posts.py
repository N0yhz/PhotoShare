import logging
import logging
from typing import List

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.orm import Query, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db

from src.entity.models import Post, Tag, User, RoleEnum

from src.schemas.tags import TagCreate, TagList, AddTags
from src.schemas.posts import PostOut, PostUpdate, PostCreate, MessageResponse, PostTags

from src.services.cloudinary import CloudinaryService
from src.services.utils import get_current_user, RoleChecker

from src.repository.posts import PostRepository

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/create", response_model=PostOut)
async def create_post(
    file: UploadFile = File(...),
    description: str = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new post with an uploaded image.

    Args:
        file (UploadFile): The image file to upload.
        description (str, optional): A description for the post.
        db (AsyncSession): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        PostOut: The created post.

    Raises:
        HTTPException: If there is an error during post creation or file upload.
    """
    try:
        cloudinary_url = await CloudinaryService.upload_image(file)
        new_post = await PostRepository.create_post(db, PostCreate(description=description, cloudinary_url=cloudinary_url), user_id=current_user.id)
        return new_post
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/all_posts")
async def get_posts(
    db: AsyncSession = Depends(get_db),
):
    """
    Get all posts from the database.

    Args:
        db (AsyncSession): The database session.

    Returns:
        List[Post]: A list of all posts in the database.
    """
    posts = await PostRepository.get_all_posts(db)
    return posts


@router.get("/", response_model=List[PostOut])
async def get_posts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Gets all posts created by the current authenticated user.

    Args:
        db (AsyncSession): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        List[PostOut]: A list of posts created by the current user.
    """
    posts = await PostRepository.get_by_user(db, current_user.id)
    return posts


@router.get("/{post_id}", response_model=PostOut)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Gets a specific post by its ID, including its associated tags.

    Args:
        post_id (int): The ID of the post.
        db (AsyncSession): The database session.

    Returns:
        PostOut: The post with its details.

    Raises:
        HTTPException: If the post is not found.
    """
    post = await PostRepository.get_with_tags(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.post("/posts/{post_id}/tags", response_model=PostTags)
async def add_tags_to_post(post_id: int, tags: AddTags, db: AsyncSession = Depends(get_db)):
    """
    Add tags to a specific post.

    Args:
        post_id (int): The ID of the post.
        tags (AddTags): The tags to add to the post.
        db (AsyncSession): The database session.

    Returns:
        PostTags: The updated post with its tags.

    Raises:
        HTTPException: If more than 5 tags are added or another error occurs.
    """

    if len(tags.tags) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can add up to 5 tags only"
        )

    updated_post = await PostRepository.add_tags_to_post(db=db, post_id=post_id, tags=tags.tags)
    return updated_post


@router.put("/{post_id}", response_model=PostOut)
async def update_post(
    post_id: int,
    data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update the description of a specific post.

    Args:
        post_id (int): The ID of the post to update.
        data (PostUpdate): The updated data for the post.
        current_user (User): The currently authenticated user.
        db (AsyncSession): The database session.

    Returns:
        PostOut: The updated post.

    Raises:
        HTTPException: If the post is not found or the user is not authorized to update it.
    """
    post = await PostRepository.get_post(db, post_id)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to update this post")

    updated_post = await PostRepository.update_post(
        db=db,
        post_id=post_id,
        description=data.description,
    )
    return updated_post


@router.delete("/{post_id}", response_model=MessageResponse)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a specific post.

    Args:
        post_id (int): The ID of the post to delete.
        current_user (User): The currently authenticated user.
        db (AsyncSession): The database session.

    Returns:
        MessageResponse: A message indicating successful deletion.

    Raises:
        HTTPException: If the post is not found or the user is not authorized to delete it.
    """
    post = await PostRepository.get_post(db, post_id)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to delete this post")

    deleted_post = await PostRepository.delete_post(db, post_id)
    if deleted_post:
        return {"message": "Post deleted successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete post")


@router.get("/secret_for_all")
async def read_secret(
    user: User = Depends(RoleChecker([RoleEnum.user, RoleEnum.moderator, RoleEnum.admin])),
):
    """
    Get a secret message for all authenticated users.

    Args:
        user (User): The currently authenticated user.

    Returns:
        dict: A secret message.
    """
    return {"message": "Secret message for all authenticated users"}


@router.get("/secret_for_moderators")
async def read_secret(
    user: User = Depends(RoleChecker([RoleEnum.moderator, RoleEnum.admin])),
):
    """
    Get a secret message for moderators and admins.

    Args:
        user (User): The currently authenticated user.

    Returns:
        dict: A secret message.
    """
    return {"message": "Secret message for moderators"}


@router.get("/secret_for_admin")
async def read_secret(
    user: User = Depends(RoleChecker([RoleEnum.admin])),
):
    """
    Get a secret message for admins only.

    Args:
        user (User): The currently authenticated admin user.

    Returns:
        dict: A secret message.
    """
    return {"message": "Secret message for admin"}