import cloudinary
import cloudinary.uploader
import cloudinary.api


# Initialize Cloudinary
cloudinary.config(
    cloud_name="your_cloud_name",
    api_key="your_api_key",
    api_secret="your_api_secret"
)


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
