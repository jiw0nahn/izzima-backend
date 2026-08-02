from typing import Any

from blip import generate_caption
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
    ) -> dict[str, Any]:
        if not image_bytes:
            raise ValueError("이미지 바이트가 비어 있습니다.")

        # 1. OCR 실행
        ocr_result = self.ocr_service.extract_text(image_bytes)
        ocr_text = ocr_result["full_text"]

        if not isinstance(ocr_text, str):
            raise TypeError(
                "ocr_result['full_text']는 문자열이어야 합니다."
            )

        # 2. BLIP 캡션 생성
        caption = generate_caption(image_bytes)

        # 3. OCR 텍스트와 BLIP 캡션을 Qwen에 전달
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


# OCR과 Qwen 모델을 매번 새로 만들지 않도록
# 파이프라인 인스턴스를 모듈 로딩 시 한 번만 생성한다.
_pipeline = AIPipeline()


def run_pipeline(
    image_bytes: bytes,
) -> dict[str, Any]:
    """
    백엔드에서 호출하는 AI 파이프라인 진입 함수.

    처리 순서:
    이미지 bytes → OCR + BLIP → Qwen → Event
    """
    return _pipeline.run(
        image_bytes=image_bytes,
    )