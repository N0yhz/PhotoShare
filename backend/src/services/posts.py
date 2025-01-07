from typing import List
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.cloudinary import CloudinaryService
from src.repository import posts as PostRepository

class PostService:

    async def upload_post(
        file: UploadFile,
        user_id: int, 
        description: str = None,
        tags: List[str] = None
    ):
        contents = await file.read()
        upload_result = await CloudinaryService.upload_image(contents)

        # Create post in database
        post = await PostRepository.create_post(
            user_id=user_id,
            cloudinary_url=upload_result["secure_url"],
            description=description
        )

        # Add tags if provided
        if tags:
            await PostRepository.add_tags(post, tags)

        return post
    
    async def delete_post(self, db: AsyncSession, post_id: int, user_id: int):
        """
        Delete a post and its associated image.
        :param post_id: ID of the post to delete.
        :param user_id: ID of the user requesting deletion.
        """
        post = await self.post_repository.get(db, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        if post.user_id != user_id:
            raise HTTPException(status_code=404, detail="Not authorized to delete this post")
        await self.post_repository.delete(db, post_id)
