from pydantic import BaseModel

class ImageResponse(BaseModel):
    """
     Schema for the response containing Cloudinary and QR code URLs.

     Attributes:
         cloudinary_url (str): The URL of the image stored in Cloudinary.
         qr_code_url (str): The URL of the generated QR code for the image.
     """
    cloudinary_url: str
    qr_code_url: str
