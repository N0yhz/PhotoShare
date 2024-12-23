import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes.auth import router as auth_router
from src.routes.photos import router as photos_router


app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(photos_router, prefix="/photos", tags=["photos"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to PhotoShare"}