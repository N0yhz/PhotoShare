import os
import uvicorn
from fastapi import FastAPI
from src.routes.image_routes import router as image_router

app = FastAPI()
app.include_router(image_router, prefix="/images", tags=["Images"])


@app.get("/")
def read_root():
    return {"message": "Welcome to PhotoShare"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), log_level="info")