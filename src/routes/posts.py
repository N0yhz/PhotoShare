import json
import shutil
import tempfile
import requests
from typing import List
from pathlib import Path

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db

from src.entity.models import Post, Tag, User, RoleEnum, Transformation

from src.schemas.tags import TagCreate
from src.schemas.posts import PostOut, PostUpdate, PostCreate
from src.schemas.cloudinary_qr import ImageResponse

from src.services.cloudinary import CloudinaryService
from src.services.utils import get_current_user, RoleChecker
from src.services.qr_code import generate_qr_code
from src.services.posts import PostService

from src.repository.posts import PostRepository

router = APIRouter()


@router.post("/", response_model=PostOut)
async def upload_post(
    file: UploadFile = File(...),
    data: PostCreate = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Uploads an image, creates a post with description and tags, and returns the post with the image URL.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    
    # Use tempfile for platform-independent temporary file handling
    # Temporary file storage location
    temp_file = Path(f"/tmp/{file.filename}")
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Upload the image to Cloudinary
    try:
        cloudinary_url = await CloudinaryService.upload_image(temp_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")
    finally:
        temp_file.unlink()

    # Create post in the database with the image URL
    post_repo = PostRepository(db)
    post_service = PostService(post_repo)

    post = await post_service.upload_post(
        file=file,
        user_id=current_user.id,
        description=data.description,
        tags=data.tags,
        cloudinary_url=cloudinary_url
    )

    return post

@router.get("/", response_model=List[PostOut])
async def get_posts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all posts created by the current user.
    """
    post_repo = PostRepository(db)
    posts = await post_repo.get_by_user(current_user.id)
    return posts

@router.get("/{post_id}", response_model=PostOut)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific post by its ID, including its associated tags.
    """
    post_repo = PostRepository(db)
    post = await post_repo.get_with_tags(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post

@router.put("/{post_id}", response_model=PostOut)
async def update_post(
    post_id: int,
    data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a post's description and tags if the current user owns it.
    """
    post_repo = PostRepository(db)
    post = await post_repo.get(post_id)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.user_id!= current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to update this post")
    
    updated_post = await post_repo.update(
        post_id = post_id,
        description = data.description,
    )

    if data.tags is not None:
        await post_repo.add_tags(updated_post, data.tags)

    return updated_post

@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a post if the current user owns it.
    """

    post_repo = PostRepository(db)
    post_service = PostService(post_repo)

    await post_service.delete_post(post_id, current_user.id)
    return {"message": "Post deleted successfully"}


@router.post("/{post_id}/tags/", response_model=PostOut)
async def add_tags_to_post(
    post_id: int,
    tags: List[TagCreate], 
    db: AsyncSession = Depends(get_db)
    ):
    """
    Add tags to a specific post. Up to 5 tags can be added.
    """
    if len(tags) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="You can add up to 5 tags only"
        )

    post_repo = PostRepository(db)
    post = await post_repo.get_with_tags(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    try:
        for tag_data in tags:
            tag = await db.scalar(select(Tag).where(Tag.name == tag_data.name).limit(1))
            if not tag:
                tag = Tag(name=tag_data.name)
                db.add(tag)
                await db.commit()
                await db.refresh(tag)

            if tag not in post.tags:
                post.tags.append(tag)

        await db.commit()
        await db.refresh(post)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding tags to post: {str(e)}"
        )
    
    return post

@router.post("/transform/{post_id}", response_model=ImageResponse)
async def transform_image_with_cloudinary(
    post_id: int,
    effect: int = Form(..., description="Choose 1 (grayscale) or 2 (cartoon)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Transforms an image file with a predefined effect and generates a QR code URL.
    """
    # Get the image URL from the database
    query = select(Post).where(Post.id == post_id)
    result = await db.execute(query)
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Get the image file from Cloudinary
    try:
        cloudinary_url = post.cloudinary_url  # Get the Cloudinary URL from the database
        response = requests.get(cloudinary_url)  # Download the image from Cloudinary
        response.raise_for_status()
        file = response.content  # Get the image file in bytes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching image: {str(e)}")

    # Choosing the effect based on the user input
    transformations = []
    if effect == 1:
        transformations.append({"effect": "grayscale"})
    elif effect == 2:
        transformations.append({"effect": "cartoonify"})
    else:
        raise HTTPException(status_code=400, detail="Invalid effect. Choose 1 (grayscale) or 2 (cartoon).")

    # Convert transformations to string
    transformation_params_str = json.dumps(transformations)  # Save as JSON string

    temp_file = Path(f"/tmp/{post_id}_image.jpg")
    with open(temp_file, "wb") as buffer:
        buffer.write(file)

    # Transform the image using Cloudinary
    try:
        transformed_url = CloudinaryService.upload_image(temp_file, transformations)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error transforming image: {str(e)}")
    finally:
        temp_file.unlink()

    # Save the transformed URL to the database
    new_transformation = Transformation(
        transform_params=transformation_params_str,
        transformed_url=transformed_url,
        post_id=post_id)
    db.add(new_transformation)
    await db.commit()
    await db.refresh(new_transformation)

    # Generate a QR code for the transformed URL
    qr_code_image = generate_qr_code(transformed_url)

    # Save the QR code to a temporary file
    qr_code_path = f"/tmp/{post_id}_qrcode.png"
    with open(qr_code_path, "wb") as qr_file:
        qr_file.write(qr_code_image.read())

    # Upload the QR code to Cloudinary
    try:
        qr_code_url = CloudinaryService.upload_image(qr_code_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading QR code: {str(e)}")
    finally:
        qr_code_path.unlink()

    return ImageResponse(cloudinary_url=transformed_url, qr_code_url=qr_code_url)

@router.get("/secret_for_all")
async def read_secret(
    user: User = Depends(RoleChecker([RoleEnum.user, RoleEnum.moderator, RoleEnum.admin])),
):
    return {"message": "Secret message for all authenticated users"}


@router.get("/secret_for_moderators")
async def read_secret(
    user: User = Depends(RoleChecker([RoleEnum.moderator, RoleEnum.admin])),
):
    return {"message": "Secret message for moderators"}


@router.get("/secret_for_admin")
async def read_secret(
    user: User = Depends(RoleChecker([RoleEnum.admin])),
):
    return {"message": "Secret message for admin"}