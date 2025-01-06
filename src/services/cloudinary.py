import os
import asyncio
import logging
import cloudinary
from fastapi import HTTPException, UploadFile

from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

# Initialize Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

class CloudinaryService:
    @staticmethod
    async def upload_image(file: UploadFile) -> str:
        try:
            result = await asyncio.to_thread(
                cloudinary.uploader.upload,file.file, folder="photoshare"
                )
            logger.info("Image uploaded successfully")
            return result['secure_url']
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def upload_image_to_transform(file_path: str, transformation: dict = None) -> str:
        try:
            with open(file_path, "rb") as f:
                result = await asyncio.to_thread(
                    cloudinary.uploader.upload, f, folder="pts_transform", transformation=transformation
                )
            logger.info("Image uploaded successfully")
            return result['secure_url']
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))