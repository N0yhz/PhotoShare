import logging
import logging
from typing import List

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db

from src.entity.models import Tag, User, RoleEnum

from src.schemas.tags import AddTags
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
    Creates a new post with an uploaded image and description.

    Args:
        file (UploadFile): The image file to upload.
        description (str, optional): The description of the post. Defaults to None.
        db (AsyncSession, optional): The database session for executing queries. Defaults to dependency injection of get_db.
        current_user (User, optional): The currently authenticated user. Defaults to dependency injection of get_current_user.

    Returns:
        PostOut: The newly created post.

    Raises:
        HTTPException: If an error occurs while creating the post.
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
    Retrieves all posts from the database.

    Args:
        db (AsyncSession, optional): The database session for executing queries. Defaults to dependency injection of get_db.

    Returns:
        List[Post]: A list of all posts.
    """
    posts = await PostRepository.get_all_posts(db)
    return posts

@router.get("/", response_model=List[PostOut])
async def get_posts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves all posts created by the current user.

    Args:
        db (AsyncSession, optional): The database session for executing queries. Defaults to dependency injection of get_db.
        current_user (User, optional): The currently authenticated user. Defaults to dependency injection of get_current_user.

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
    Retrieve a specific post by its ID, including its associated tags.

    Args:
        post_id (int): The ID of the post to retrieve.
        db (AsyncSession, optional): The database session for executing queries. Defaults to dependency injection of get_db.

    Returns:
        PostOut: The post object if found, otherwise raises HTTPException.

    Raises:
        HTTPException: If the post is not found.
    """
    post = await PostRepository.get_with_tags(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.post("/{post_id}/tags", response_model=PostTags)
async def add_tags_to_post(post_id: int, tags: AddTags, db: AsyncSession = Depends(get_db)):
    """
    Adds tags to a specific post.

    Args:
        post_id (int): The ID of the post to add tags to.
        tags (AddTags): The tags to add.
        db (AsyncSession, optional): The database session for executing queries. Defaults to dependency injection of get_db.

    Returns:
        PostTags: The updated post with added tags.

    Raises:
        HTTPException: If more than 5 tags are provided.
    """
    if len(tags.tags) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can add up to 5 tags only"
        )

    updated_post = await PostRepository.add_tags_to_post(db=db, post_id=post_id, tags=tags.tags)
    return updated_post

@router.get('/by-tags/{tag_id}')
async def get_posts_by_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db)
):
    tag_result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = tag_result.scalars().first()

    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    
    posts = await PostRepository.get_posts_by_tag(db, tag_id)
    return posts

@router.post("/by-tags/{tag_name}")
async def get_posts_by_tag_name(
    tag_name: str,
    db: AsyncSession = Depends(get_db)
):
    tag_result = await db.execute(select(Tag).where(Tag.name == tag_name))
    tag = tag_result.scalars().first()
    
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    
    posts = await PostRepository.get_posts_by_tag(db, tag.id)
    return posts



@router.put("/{post_id}", response_model=PostOut)
async def update_post(
    post_id: int,
    data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Updates the description of a specific post.

    Args:
        post_id (int): The ID of the post to update.
        data (PostUpdate): The new description data.
        current_user (User, optional): The currently authenticated user. Defaults to dependency injection of get_current_user.
        db (AsyncSession, optional): The database session for executing queries. Defaults to dependency injection of get_db.

    Returns:
        PostOut: The updated post object.

    Raises:
        HTTPException: If the post is not found or the user is not authorized to update the post.
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
    Deletes a specific post.

    Args:
        post_id (int): The ID of the post to delete.
        current_user (User, optional): The currently authenticated user. Defaults to dependency injection of get_current_user.
        db (AsyncSession, optional): The database session for executing queries. Defaults to dependency injection of get_db.

    Returns:
        MessageResponse: A message indicating successful deletion of the post.

    Raises:
        HTTPException: If the post is not found or the user is not authorized to delete the post.
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
    Retrieves a secret message for all authenticated users.

    Args:
        user (User, optional): The currently authenticated user. Defaults to dependency injection of RoleChecker([RoleEnum.user, RoleEnum.moderator, RoleEnum.admin]).

    Returns:
        dict: A dictionary containing the secret message.
    """
    return {"message": "Secret message for all authenticated users"}


@router.get("/secret_for_moderators")
async def read_secret(
    user: User = Depends(RoleChecker([RoleEnum.moderator, RoleEnum.admin])),
):
    """
    Retrieves a secret message for moderators.

    Args:
        user (User, optional): The currently authenticated user. Defaults to dependency injection of RoleChecker([RoleEnum.moderator, RoleEnum.admin]).

    Returns:
        dict: A dictionary containing the secret message.
    """
    return {"message": "Secret message for moderators"}


@router.get("/secret_for_admin")
async def read_secret(
    user: User = Depends(RoleChecker([RoleEnum.admin])),
):
    """
    Retrieves a secret message for admin users.

    Args:
        user (User, optional): The currently authenticated user. Defaults to dependency injection of RoleChecker([RoleEnum.admin]).

    Returns: dict: A dictionary containing the secret message.
    """
    return {"message": "Secret message for admin"}
