from embedding import EmbeddingService


service = EmbeddingService()

text = (
    "WATERBOMB SEOUL 2025 공연 콘서트 행사 "
    "2025-07-05 13:00 킨텍스 제2전시장"
)

embedding = service.embed(text)

print("text:", text)
print("dimension:", len(embedding))
print("sample:", embedding[:5])