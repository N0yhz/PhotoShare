from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.database.db import get_db
from backend.src.entity.models import Tag
from backend.src.schemas.tags import TagOut, TagCreate

router = APIRouter()


@router.post("", response_model=TagOut)
async def create_tag(tag: TagCreate, session: AsyncSession = Depends(get_db)):
    """ Creates a new tag in the database.

    Args:
        tag (TagCreate): The tag creation data.
        session (AsyncSession, optional): The database session for executing queries. Defaults to dependency injection of get_db.

    Returns:
        TagOut: The newly created tag or the existing tag if it already exists.

    Raises:
        HTTPException: If an error occurs while creating the tag.
    """
    existing_tag = await session.scalar(select(Tag).where(Tag.name == tag.name).limit(1))

    if existing_tag:
        return existing_tag

    db_tag = Tag(name=tag.name)
    session.add(db_tag)
    await session.commit()
    await session.refresh(db_tag)

    return db_tag
