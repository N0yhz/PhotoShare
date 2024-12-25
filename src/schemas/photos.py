from datetime import datetime
from pydantic import BaseModel, Field


class CreatePost(BaseModel):
    cloudinary_url: str = Field(max_length=255)
    description: str = Field(max_length=250)
    user_id: int


class ResponsePost(BaseModel):
    id: int
    cloudinary_url: str
    description: str
    create_at: datetime
    update_at: datetime

    class Config:
        from_attributes = True
