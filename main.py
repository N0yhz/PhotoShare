import uvicorn
from fastapi import FastAPI
from src.routes import tags, posts
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.include_router(tags.router, prefix='/api')
app.include_router(posts.router, prefix='/api')

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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)