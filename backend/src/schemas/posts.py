from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from .tags import TagOut

class PostBase(BaseModel):
    cloudinary_url: str
    description: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    description: Optional[str] = None

class PostOut(BaseModel):
    id: int
    user_id: int
    cloudinary_url: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    tags: List[TagOut]
 
    model_config = ConfigDict(from_attributes = True, arbitrary_types_allowed=True)

class PostTags(PostOut):
    tags: List[TagOut]

class MessageResponse(BaseModel):
    message: str