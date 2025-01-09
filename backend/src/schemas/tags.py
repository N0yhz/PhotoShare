from pydantic import BaseModel, Field, ConfigDict
from typing import List


class TagBase(BaseModel):
    """
    Base schema for tags.

    Attributes:
        name (str): The name of the tag, with a maximum length of 150 characters.
    """
    name: str = Field(max_length=150)

class TagCreate(TagBase):
    """
    Schema for creating a new tag.

    Inherits:
        TagBase
    """
    pass

class TagOut(BaseModel):
    """
    Schema for the response containing tag details.

    Attributes:
        id (int): The unique identifier of the tag, must be greater than 0.
        name (str): The name of the tag.
    """
    id: int = Field(gt=0)
    name: str

    model_config = ConfigDict(from_attributes = True)

class AddTags(BaseModel):
    """
    Schema for adding multiple tags to a resource.

    Attributes:
        tags (List[str]): A list of tag names to be added.
    """
    tags: List[str]

class TagList(BaseModel):
    """
    Schema for a response containing a list of tag names.

    Attributes:
        tags (List[str]): A list of tag names.
    """
    tags: List[str]