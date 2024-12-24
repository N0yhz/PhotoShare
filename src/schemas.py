from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    name: str = Field(max_length=150)


class TagOut(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(max_length=150)


class PostOut(BaseModel):
    id: int = Field(gt=0)
    tags: list[TagOut]

    class Config:
        orm_mode = True