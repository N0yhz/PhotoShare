from typing import List
from fastapi import UploadFile, HTTPException
from src.repository.posts import PostRepository
from src.services.cloudinary import CloudinaryService

class PostService:
    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo
        self.cloudinary = CloudinaryService

    async def upload_post(
            self,
            file: UploadFile,
            user_id: int, 
            description: str = None,
            tags: List[str] = None,
            cloudinary_url: str = None
    ):
        """
        Upload an image and create a post in the database.
        :param file: The uploaded image file.
        :param user_id: ID of the user creating the post.
        :param description: Description of the post.
        :param tags: Tags for the post.
        :return: The created post.
        """
        contents = await file.read()
        
        cloudinary_url = await self.cloudinary.upload_image(contents)

        #  Create a new post in the database
        try:
            post =  await self.post_repo.create(
                user_id=user_id,
                cloudinary_url=cloudinary_url,
                description=description
            )

            if tags:
                await self.post_repo.add_tags(post, tags)
            return post
        except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error creating post: {str(e)}")
    
    async def delete_post(self, post_id: int, user_id: int):
        """
        Delete a post and its associated image.
        :param post_id: ID of the post to delete.
        :param user_id: ID of the user requesting deletion.
        """
        post = await self.post_repo.get(post_id)
        if not post or post.user_id != user_id:
            raise HTTPException(status_code=404, detail="Post not found or not owned by the user")
        
        public_id = post.cloudinary_url.split("/")[-1].split["."][0]

        try:
            await self.cloudinary.delete_image(public_id)

            await self.post_repo.delete(post_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting post: {str(e)}")