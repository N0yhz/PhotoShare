from typing import Any

from pydantic import ConfigDict, field_validator, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://tbb:pt_project@db:5432/photo_share"
    SECRET_KEY: str = "0784904923432bhf437845f"
    ALGORITHM: str = "HS256"
    # MAIL_USERNAME: EmailStr = ""
    # MAIL_PASSWORD: str = ""
    # MAIL_FROM: str = ""
    # MAIL_PORT: int = 
    # MAIL_SERVER: str = ""
    REDIS_HOST: str = 'redis'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    CLOUDINARY_CLOUD_NAME: str = "dbliiwnzm"
    CLOUDINARY_API_KEY: int = 523943651299381
    CLOUDINARY_API_SECRET: str = "c560Dpun32RjksjoA1JNjSBeGzY"
    
    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v: Any):
        if v not in ["HS256", "HS512"]:
            raise ValueError("algorithm must be HS256 or HS512")
        return v


    model_config = ConfigDict(extra='ignore', env_file=".env", env_file_encoding="utf-8")


config = Settings()

