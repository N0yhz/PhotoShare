from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from .tags import TagOut

class PostBase(BaseModel):
    description: Optional[str] = None

class PostCreate(PostBase):
    tags: Optional[List[str]] = None

class PostUpdate(BaseModel):
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class PostOut(PostBase):
    id: int
    user_id: int
    cloudinary_url: str
    created_at: datetime
    updated_at: datetime
    tags: List[TagOut] = []
 
    class Config:
        from_attributes = True