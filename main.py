from fastapi import FastAPI

from app.routers import events, images, search

app = FastAPI(
    title="졸크크 AI 갤러리 백엔드",
    description="이미지 업로드/조회 API. AI Pipeline 연동 전까지 ocr_text/caption/category/search_text는 null.",
    version="0.1.0",
)

app.include_router(images.router)
app.include_router(events.router)
app.include_router(search.router)


@app.get("/")
def read_root():
    return {"message": "FastAPI 서버 정상 작동 중"}
