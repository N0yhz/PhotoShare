from datetime import datetime
from pydantic import BaseModel, ConfigDict

class CommentBase(BaseModel):
    """
    Base schema for comments.

    Attributes:
        content (str): The content of the comment.
    """
    content: str

class CommentCreate(CommentBase):
    """
    Schema for creating a new comment.

    Inherits:
        CommentBase
    """
    pass

class CommentUpdate(BaseModel):
    """
    Schema for updating an existing comment.

    Attributes:
        content (str): The updated content of the comment.
    """
    content: str

class CommentOut(BaseModel):
    """
    Schema for the response containing comment details.

    Attributes:
        id (int): The unique identifier of the comment.
        user_id (int): The unique identifier of the user who created the comment.
        post_id (int): The unique identifier of the post the comment belongs to.
        content (str): The content of the comment.
        created_at (datetime): The timestamp when the comment was created.
        updated_at (datetime): The timestamp when the comment was last updated.
        """
    id: int
    user_id: int
    post_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes = True)
