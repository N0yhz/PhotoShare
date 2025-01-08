from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import Tag
from src.schemas.tags import TagOut, TagCreate

router = APIRouter()


@router.post("", response_model=TagOut)
async def create_tag(tag: TagCreate, session: AsyncSession = Depends(get_db)):
    """
    Creates a new tag or returns an existing tag if it already exists.

    Args:
        tag (TagCreate): The tag data to create.
        session (AsyncSession): The database session.

    Returns:
        TagOut: The created or existing tag.

    Raises:
        None: This function does not explicitly raise exceptions.
    """
    existing_tag = await session.scalar(select(Tag).where(Tag.name == tag.name).limit(1))

    if existing_tag:
        return existing_tag

    db_tag = Tag(name=tag.name)
    session.add(db_tag)
    await session.commit()
    await session.refresh(db_tag)

    return db_tag
