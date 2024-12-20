import enum
from datetime import date

from typing import Optional, List
from sqlalchemy import DateTime, ForeignKey, Integer, String, Enum, Boolean, Text, func, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.db import Base

class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"

post_tags= Table(
    "post_tags",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id")),
    Column("tag_id", Integer, ForeignKey("tags.id"))
)

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    verification_token: Mapped[str] = mapped_column(String(155), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    role: Mapped[Enum] = mapped_column("role", Enum(Role), default=Role.user, nullable=True)
    avatar: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(50))
    last_name: Mapped[Optional[str]] = mapped_column(String(50))
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    #relationships
    posts: Mapped[List["Post"]] = relationship("Post", back_populates="user")
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="user")

class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cloudinary_url: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text(300), nullable=True)
    created_at: Mapped[date] = mapped_column(
        "created_at", DateTime, default=func.now(), nullable=True
    )
    updated_at: Mapped[date] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now(), nullable=True
    )

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="posts")
    comments: Mapped["Comment"] = relationship("Comment", back_populates="post")
    tags: Mapped[List["Tag"]] = relationship(secondary=post_tags, back_populates="posts")
    transformations: Mapped[List["Transformation"]] = relationship("Transformation", back_populates="post")

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    posts: Mapped[List["Post"]] = relationship("Post", secondary="post_tags", back_populates="tags")

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text(255), nullable=False)
    created_at: Mapped[date] = mapped_column(
        "created_at", DateTime, default=func.now(), nullable=True
    )
    updated_at: Mapped[date] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now(), nullable=True
    )

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id", nullable=True))

    #relationship
    user: Mapped["User"] = relationship("User", back_populates="comments")
    post: Mapped["Post"] = relationship("Post", back_populates="comments")

class Transformation(Base):
    __tablename__ = "transformations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    transform_params: Mapped[str] = mapped_column(String(255), nullable=False)
    transformed_url: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[date] = mapped_column(
        "created_at", DateTime, default=func.now(), nullable=True
    )
    
    photo_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id"), nullable=False)

    photo: Mapped["Post"] = relationship("Post", back_populates="transformations")
    qr_codes: Mapped["QRCode"] = relationship("QRCode", back_populates="transformation")

class QRCode(Base):
    __tablename__ = "qr_codes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    qr_code_url: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[date] = mapped_column(
        "created_at", DateTime, default=func.now(), nullable=True
    )

    transformation_id: Mapped[int] = mapped_column(Integer, ForeignKey("transformations.id"), nullable=False)
    transformation: Mapped["Transformation"] = relationship("Transformation", back_populates="qr_codes")