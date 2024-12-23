from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.entity.models import Post, Tag
from src.schemas import TagCreate, PostOut

router = APIRouter(prefix='/posts', tags=["posts"])


@router.post("/{post_id}/tags/", response_model=PostOut)
async def add_tags_to_post(post_id: int, tags: List[TagCreate], session: Session = Depends(get_db)):
    if len(tags) > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can add up to 5 tags only")

    db_post = await session.scalar(select(Post).where(Post.id == post_id).limit(1))
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    for tag in tags:
        db_tag = await session.scalar(select(Tag).where(Tag.name == tag.name).limit(1))
        if not db_tag:
            db_tag = Tag(name=tag.name)
            session.add(db_tag)
            await session.commit()
            await session.refresh(db_tag)
        if db_tag not in db_post.tags:
            db_post.tags.append(db_tag)

    await session.commit()
    await session.refresh(db_post)

    return db_post
