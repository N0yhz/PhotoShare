import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes import tags, posts, comments, auth, cloudinary_routes

app = FastAPI()

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(tags.router, prefix='/api/tags', tags=["Tags"])
app.include_router(posts.router, prefix='/api/posts', tags=["Posts"])
app.include_router(comments.router, prefix="/api/comments", tags=["Comments"])
app.include_router(cloudinary_routes.router, prefix="/api/transform", tags=["Transformations"])

origins = ["http://localhost:3000",
           "http://127.0.0.1:3000",
           ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to PhotoShare"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)