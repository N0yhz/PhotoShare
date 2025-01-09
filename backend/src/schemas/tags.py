from pydantic import BaseModel, Field, ConfigDict
from typing import List


class TagBase(BaseModel):
    name: str = Field(max_length=150)

class TagCreate(TagBase):
    pass


class TagOut(BaseModel):
    id: int = Field(gt=0)
    name: str

    model_config = ConfigDict(from_attributes=True)

class AddTags(BaseModel):
    tags: List[str]

class TagList(BaseModel):
    tags: List[str]