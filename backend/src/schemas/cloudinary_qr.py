from pydantic import BaseModel

class ImageResponse(BaseModel):
    cloudinary_url: str
    qr_code_url: str
