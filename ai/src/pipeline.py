from typing import Any

from blip import generate_caption
from embedding import EmbeddingService
from models import Event
from ocr import OCRService
from postprocess.processor import postprocess_event
from qwen import QwenService


PRIMARY_MODEL = "qwen3.5:9b"
FALLBACK_MODEL = "qwen3.5:27b"


class AIPipeline:
    def __init__(self) -> None:
        self.ocr_service = OCRService()

        self.embedding_service = EmbeddingService()

        # 기본 모델
        self.primary_qwen_service = QwenService(
            model_name=PRIMARY_MODEL,
        )

        # 어려운 경우에만 사용하는 큰 모델
        self.fallback_qwen_service = QwenService(
            model_name=FALLBACK_MODEL,
        )

    @staticmethod
    def _should_fallback(
        event: Event,
        ocr_text: str,
    ) -> tuple[bool, list[str]]:
        """
        9B 결과가 충분히 신뢰하기 어려운 경우
        27B를 다시 호출할지 판단한다.

        너무 공격적인 규칙은 넣지 않고,
        현재까지 실제 테스트에서 확인된
        명확한 실패 패턴 위주로 판단한다.
        """

        reasons: list[str] = []

        metadata = event.metadata

        if event.type != "none":
            core_fields = [
                event.title,
                event.date,
                event.time,
                event.location,
            ]

            core_value_count = sum(
                value is not None
                and str(value).strip() != ""
                for value in core_fields
            )

            if core_value_count <= 1:
                reasons.append(
                    "핵심 이벤트 필드가 지나치게 부족함"
                )

        if event.type == "reservation":

            if (
                event.location is None
                and metadata.reservation_number is None
            ):
                reasons.append(
                    "예약 정보에서 장소와 예약번호가 모두 누락됨"
                )

            invalid_status_values = {
                "예매취소",
                "예약취소",
                "취소하기",
                "좌석보기",
                "선물하기",
            }

            if (
                metadata.status is not None
                and metadata.status.strip()
                in invalid_status_values
            ):
                reasons.append(
                    "버튼 텍스트가 status로 추출됨"
                )

        if event.type == "performance":

            if event.title is None:
                reasons.append(
                    "공연 제목이 누락됨"
                )

            if event.date is None:
                reasons.append(
                    "공연 날짜가 누락됨"
                )

        if event.type == "expiration":

            if event.date is None:
                reasons.append(
                    "만료 이벤트의 유효기간이 누락됨"
                )

            if event.title is None:
                reasons.append(
                    "쿠폰/상품권 제목이 누락됨"
                )

        normalized_ocr = ocr_text.replace(" ", "")

        if (
            "예매번호" in normalized_ocr
            and metadata.reservation_number is None
        ):
            reasons.append(
                "OCR에 예매번호가 있지만 추출되지 않음"
            )

        if (
            "주문번호" in normalized_ocr
            and metadata.order_number is None
        ):
            reasons.append(
                "OCR에 주문번호가 있지만 추출되지 않음"
            )

        if (
            "예매자명" in normalized_ocr
            and metadata.buyer_name is None
        ):
            reasons.append(
                "OCR에 예매자명이 있지만 추출되지 않음"
            )

        if (
            "예매일" in normalized_ocr
            and metadata.purchase_date is None
        ):
            reasons.append(
                "OCR에 예매일이 있지만 추출되지 않음"
            )

        if (
            "취소마감" in normalized_ocr
            and metadata.cancellation_deadline is None
        ):
            reasons.append(
                "OCR에 취소마감 정보가 있지만 추출되지 않음"
            )

        if (
            "구매금액" in normalized_ocr
            and metadata.purchase_amount is None
        ):
            reasons.append(
                "OCR에 구매금액이 있지만 추출되지 않음"
            )

        if (
            "티켓금액" in normalized_ocr
            and metadata.ticket_amount is None
        ):
            reasons.append(
                "OCR에 티켓금액이 있지만 추출되지 않음"
            )

        return bool(reasons), reasons

    def run(
        self,
        image_bytes: bytes,
    ) -> dict[str, Any]:

        if not image_bytes:
            raise ValueError(
                "이미지 바이트가 비어 있습니다."
            )

        # 1. OCR
        ocr_result = self.ocr_service.extract_text(
            image_bytes
        )

        ocr_text = ocr_result["full_text"]

        if not isinstance(ocr_text, str):
            raise TypeError(
                "ocr_result['full_text']는 문자열이어야 합니다."
            )

        # 2. BLIP
        caption = generate_caption(
            image_bytes
        )

        # 3. 먼저 9B 실행
        primary_event: Event = (
            self.primary_qwen_service.process(
                ocr_text=ocr_text,
                caption=caption,
            )
        )

        should_fallback, fallback_reasons = (
            self._should_fallback(
                event=primary_event,
                ocr_text=ocr_text,
            )
        )

        final_event = primary_event
        used_model = PRIMARY_MODEL

        # 4. 결과가 불충분하면 27B 재실행
        if should_fallback:
            print()
            print("===== FALLBACK =====")
            print(
                f"{PRIMARY_MODEL} 결과 품질이 "
                f"충분하지 않아 {FALLBACK_MODEL}를 실행합니다."
            )

            for reason in fallback_reasons:
                print(f"- {reason}")

            final_event = (
                self.fallback_qwen_service.process(
                    ocr_text=ocr_text,
                    caption=caption,
                )
            )

            used_model = FALLBACK_MODEL

        # 5. 규칙 기반 후처리 + search_text 생성
        final_event = postprocess_event(
            event=final_event,
            ocr_text=ocr_text,
            caption=caption,
            search_text_version=1,
        )

        # 6. KURE embedding 생성
        embedding = self.embedding_service.embed(
            final_event.search_text
        )

        # 7. 최종 반환
        return {
            "ocr_result": ocr_result,
            "ocr_text": ocr_text,
            "caption": caption,
            "event": final_event.model_dump(),
            "embedding": embedding,

            # 테스트/디버깅용
            "used_model": used_model,
            "fallback_used": should_fallback,
            "fallback_reasons": fallback_reasons,
        }


_pipeline = AIPipeline()


def run_pipeline(
    image_bytes: bytes,
) -> dict[str, Any]:
    """
    백엔드에서 호출하는 AI 파이프라인 진입 함수.

    처리 순서:

    image bytes
        ↓
    OCR + BLIP
        ↓
    Qwen 9B
        ↓
    품질 검사
        ↓
    필요할 경우 Qwen 27B
        ↓
    Event
        ↓
    Postprocess
        ↓
    Search Text
        ↓
    KURE Embedding
    """

    return _pipeline.run(
        image_bytes=image_bytes,
    )