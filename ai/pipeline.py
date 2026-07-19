from ai.captioning import generate_caption
from ai.embedding import generate_embedding
from ai.ocr import extract_text
from ai.structuring import extract_structured_info


def run_pipeline(image_bytes: bytes) -> dict:
    """Full flow: OCR + caption -> structured extraction -> embedding."""
    ocr_text = extract_text(image_bytes)
    caption = generate_caption(image_bytes)
    structured = extract_structured_info(ocr_text, caption)
    embedding = generate_embedding(f"{ocr_text}\n{caption}")

    return {
        "ocr_text": ocr_text,
        "caption": caption,
        "structured": structured,
        "embedding": embedding,
    }
