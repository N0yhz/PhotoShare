from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from src.services.cloudinary import upload_image
from src.services.qr_code import generate_qr_code
from src.schemas.image_schemas import ImageResponse
import shutil
import json
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
        image_url = upload_image(temp_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")
    finally:
        temp_file.unlink()

    return {"image_url": image_url}


@router.post("/transform", response_model=ImageResponse)
async def transform_image_with_cloudinary(
    file: UploadFile = File(...),
    request: str = Form(...)
):
    """
    Transforms an image file and generates a QR code for the transformed image URL.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    try:
        request_data = json.loads(request)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in request")

    transformations = request_data.get("transformations")

    temp_file = Path(f"/tmp/{file.filename}")
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Transform the image using Cloudinary
    try:
        transformed_url = upload_image(temp_file, transformations)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error transforming image: {str(e)}")
    finally:
        temp_file.unlink()

    # Generate a QR code for the transformed URL
    qr_code_image = generate_qr_code(transformed_url)

    # Save the QR code to a temporary file
    qr_code_path = f"/tmp/{file.filename}_qrcode.png"
    with open(qr_code_path, "wb") as qr_file:
        qr_file.write(qr_code_image.read())

    # Upload the QR code to Cloudinary
    qr_code_url = upload_image(qr_code_path)

    return ImageResponse(image_url=transformed_url, qr_code_url=qr_code_url)
