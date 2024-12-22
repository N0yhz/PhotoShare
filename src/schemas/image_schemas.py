from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict


class ImageUploadRequest(BaseModel):
    transformations: Optional[List[Dict[str, str]]] = None


class ImageResponse(BaseModel):
    image_url: HttpUrl
    qr_code_url: HttpUrl
