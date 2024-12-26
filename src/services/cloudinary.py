import os
import cloudinary
import cloudinary.uploader
import cloudinary.api

from fastapi import HTTPException
from dotenv import load_dotenv

# Load data from .env
load_dotenv()


# Initialize Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

class CloudinaryService:
    @staticmethod
    async def upload_image(file_path: str, transformations=None):
        """
        Upload the image to Cloudinary with optional transformations.
        :param file_path: image file.
        :param transformations: Transformations for Cloudinary.
        :return: URL of the transformed image.
        """
        try:
            upload_options = {"resource_type": "image"}
            if transformations:
                upload_options["transformation"] = transformations
        
            response = cloudinary.uploader.upload(file_path, **upload_options)
            return response["secure_url"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")
        
    @staticmethod
    async def delete_image(public_id: str):
        """
        Delete an image from Cloudinary using its public ID.
        :param public_id: The public ID of the image in Cloudinary.
        """
        try:
            cloudinary.uploader.destroy(public_id, resource_type="image")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Cloudinary deletion failed: {str(e)}")