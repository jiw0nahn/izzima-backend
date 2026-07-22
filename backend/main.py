from fastapi import FastAPI

from app.routers import images

app = FastAPI()

app.include_router(images.router)


@app.get("/")
def read_root():
    return {"message": "FastAPI 서버 정상 작동 중"}
