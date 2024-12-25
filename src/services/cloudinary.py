import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
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
    def upload_image(file, transformations=None):
        """
        Upload the image to Cloudinary with optional transformations.
        :param file: image file.
        :param transformations: Transformations for Cloudinary.
        :return: URL of the transformed image.
        """
        upload_options = {"resource_type": "image"}
        if transformations:
            upload_options["transformation"] = transformations

        response = cloudinary.uploader.upload(file, **upload_options)
        return response["url"]
