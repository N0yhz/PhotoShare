from pydantic import BaseModel, Field


class TagBase(BaseModel):
    name: str = Field(max_length=150)

class TagCreate(TagBase):
    pass

class TagOut(TagBase):
    id: int = Field(gt=0)

    class Config:
        from_attributes = True