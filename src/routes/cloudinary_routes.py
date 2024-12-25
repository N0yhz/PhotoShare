import json

from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database.db import get_db
from src.entity.models import Post, Transformation
import requests
from src.services.cloudinary import CloudinaryService
from src.services.qr_code import generate_qr_code
from src.schemas.cloudinary_qr import ImageResponse
import shutil
from pathlib import Path

router = APIRouter()


@router.post("/upload", response_model=ImageResponse)
async def upload_image_to_cloudinary(file: UploadFile = File(...)):
    """
    Uploads an image file to Cloudinary without transformations.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    temp_file = Path(f"/tmp/{file.filename}")
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Upload the image to Cloudinary
    try:
        image_url = CloudinaryService.upload_image(temp_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")
    finally:
        temp_file.unlink()

    return {"image_url": image_url}


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
        image_url = post.cloudinary_url  # Get the Cloudinary URL from the database
        response = requests.get(image_url)  # Download the image from Cloudinary
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

    return ImageResponse(image_url=transformed_url, qr_code_url=qr_code_url)
