from typing import Any

from models import Event
from ocr import OCRService
from qwen import QwenService


class AIPipeline:
    def __init__(self) -> None:
        self.ocr_service = OCRService()
        self.qwen_service = QwenService()

    def run(
        self,
        image_bytes: bytes,
        caption: str | None = None,
    ) -> dict[str, Any]:
        if not image_bytes:
            raise ValueError("이미지 바이트가 비어 있습니다.")

        # 1. 이미지 바이트를 OCR에 전달
        ocr_result = self.ocr_service.extract_text(image_bytes)

        # 2. OCR 결과 딕셔너리에서 전체 텍스트만 꺼냄
        ocr_text = ocr_result["full_text"]

        if not isinstance(ocr_text, str):
            raise TypeError("ocr_result['full_text']는 문자열이어야 합니다.")

        # 3. OCR 텍스트를 Qwen에 전달
        event: Event = self.qwen_service.process(
            ocr_text=ocr_text,
            caption=caption,
        )

        # 4. 최종 결과 반환
        return {
            "ocr_result": ocr_result,
            "ocr_text": ocr_text,
            "caption": caption,
            "event": event.model_dump(),
        }


_pipeline = AIPipeline()


def run_pipeline(
    image_bytes: bytes,
    caption: str | None = None,
) -> dict[str, Any]:
    """
    백엔드에서 호출할 함수.

    사용 예시:
        result = run_pipeline(image_bytes)
    """
    return _pipeline.run(
        image_bytes=image_bytes,
        caption=caption,
    )