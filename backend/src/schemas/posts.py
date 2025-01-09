from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from .tags import TagOut

class PostBase(BaseModel):
    """
    Base schema for posts.

    Attributes:
        cloudinary_url (str): The URL of the image stored in Cloudinary.
        description (Optional[str]): A brief description of the post. Defaults to None.
    """
    cloudinary_url: str
    description: Optional[str] = None

class PostCreate(PostBase):
    """
    Schema for creating a new post.

    Inherits:
        PostBase
    """
    pass

class PostUpdate(BaseModel):
    """
    Schema for updating an existing post.

    Attributes:
        description (Optional[str]): The updated description of the post. Defaults to None.
    """
    description: Optional[str] = None

class PostOut(BaseModel):
    """
    Schema for the response containing post details.

    Attributes:
        id (int): The unique identifier of the post.
        user_id (int): The unique identifier of the user who created the post.
        cloudinary_url (str): The URL of the image stored in Cloudinary.
        description (Optional[str]): A brief description of the post. Defaults to None.
        created_at (datetime): The timestamp when the post was created.
        updated_at (datetime): The timestamp when the post was last updated.
    """
    id: int
    user_id: int
    cloudinary_url: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    tags: List[TagOut]
 
    model_config = ConfigDict(from_attributes = True, arbitrary_types_allowed=True)

class PostTags(PostOut):
    """
    Schema for the response containing post details along with associated tags.

    Inherits:
        PostOut

    Attributes:
        tags (List[TagOut]): A list of tags associated with the post.
    """
    tags: List[TagOut]

class MessageResponse(BaseModel):
    """
    Schema for a response containing a message.

    Attributes:
        message (str): A message string, typically used for success or error responses.
    """
    message: str