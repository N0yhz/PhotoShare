import json

from fastapi import APIRouter,HTTPException, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import Post, Transformation, QRCode
import requests
from src.services.cloudinary import CloudinaryService
from src.services.qr_code import generate_qr_code
from src.schemas.cloudinary_qr import ImageResponse
from pathlib import Path

router = APIRouter()

@router.post("/{post_id}", response_model=ImageResponse)
async def transform_image_with_cloudinary(
    post_id: int,
    effect: int = Form(..., description="Choose 1 (grayscale) or 2 (cartoon)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Transforms an image from Cloudinary with the specified effect and returns the transformed image with a QR code.

    Args:
        post_id (int): The ID of the post containing the image to transform.
        effect (int): The transformation effect to apply (1 for grayscale, 2 for cartoon). Defaults to a form field.
        db (AsyncSession, optional): The database session for executing queries. Defaults to dependency injection of get_db.

    Returns:
        ImageResponse: The response containing the transformed image URL and QR code URL.

    Raises:
        HTTPException: If the post is not found, an error occurs while fetching the image, an invalid effect is specified, or an error occurs during the transformation or uploading process.
    """
    # Retrieve the post from the database
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Download the image from Cloudinary
    try:
        cloudinary_url = post.cloudinary_url
        response = requests.get(cloudinary_url)
        response.raise_for_status()
        file_content = response.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching image: {str(e)}")

    # Determine the transformation
    transformation= []
    if effect == 1:
        transformation = {"effect": "grayscale"}
    elif effect == 2:
        transformation = {"effect": "cartoonify"}
    else:
        raise HTTPException(status_code=400, detail="Invalid effect. Choose 1 (grayscale) or 2 (cartoon).")
    
    transform_params_str = json.dumps(transformation)

    # Save the image to a temporary file
    temp_file = Path(f"/tmp/{post_id}_image.jpg")
    with open(temp_file, "wb") as buffer:
        buffer.write(file_content)

    # Upload the transformed image to Cloudinary
    try:
        transformed_url = await CloudinaryService.upload_image_to_transform(str(temp_file), transformation=transformation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error transforming image: {str(e)}")
    finally:
        temp_file.unlink()

    # Create a Transformation record
    new_transformation = Transformation(
        transform_params=transform_params_str,
        transformed_url=transformed_url,
        post_id=post_id
    )
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
        qr_code_url = await CloudinaryService.upload_image_to_transform(qr_code_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading QR code: {str(e)}")
    finally:
        Path(qr_code_path).unlink()

    # Create a QRCode record
    new_qrcode = QRCode(
        qr_code_url=qr_code_url,
        transformation_id=new_transformation.id
    )
    db.add(new_qrcode)
    await db.commit()
    await db.refresh(new_qrcode)

    return ImageResponse(cloudinary_url=transformed_url, qr_code_url=qr_code_url)
