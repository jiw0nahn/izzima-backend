import re

from models import Event


def extract_amount_from_ocr(ocr_text: str) -> int | None:
    """
    OCR 텍스트에서 명확한 원화 금액을 추출한다.

    예:
    50,000원 -> 50000
    5만원 -> 50000
    5천원 -> 5000
    """

    if not ocr_text:
        return None

    won_match = re.search(
        r"(\d{1,3}(?:,\d{3})+|\d+)\s*원",
        ocr_text,
    )

    if won_match:
        return int(won_match.group(1).replace(",", ""))

    manwon_match = re.search(
        r"(\d+)\s*만원",
        ocr_text,
    )

    if manwon_match:
        return int(manwon_match.group(1)) * 10000

    cheonwon_match = re.search(
        r"(\d+)\s*천원",
        ocr_text,
    )

    if cheonwon_match:
        return int(cheonwon_match.group(1)) * 1000

    return None


def build_search_text(event: Event) -> str:
    """
    구조화된 이벤트의 핵심 필드로 검색용 텍스트를 생성한다.
    """

    parts = [
        event.title,
        event.type,
        event.date,
        event.time,
        event.location,
    ]

    return " ".join(
        str(value).strip()
        for value in parts
        if value is not None and str(value).strip()
    )


def postprocess_event(
    event: Event,
    ocr_text: str,
) -> Event:
    """
    Qwen이 추출한 Event를 규칙 기반으로 보완한다.
    """

    metadata = event.metadata.model_dump()

    if event.type == "expiration":
        amount = extract_amount_from_ocr(ocr_text)
        metadata["amount"] = amount

    updated_event = event.model_copy(
        update={
            "metadata": event.metadata.model_copy(
                update=metadata,
            ),
        }
    )

    search_text = build_search_text(updated_event)

    return updated_event.model_copy(
        update={
            "search_text": search_text,
        }
    )