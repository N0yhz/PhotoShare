from fastapi import APIRouter, Depends

from src.services.utils import RoleChecker
from src.entity.models import RoleEnum, User


router = APIRouter()

@router.get("/secret")
async def read_secret(
    user: User = Depends(RoleChecker([RoleEnum.user, RoleEnum.moderator, RoleEnum.admin])),
):
    return {"message": "Secret message from the API"}