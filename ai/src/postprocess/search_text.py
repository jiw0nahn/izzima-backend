from models import Event


EVENT_TYPE_SEARCH_TEXT = {
    "expiration": "유효기간 만료 쿠폰 상품권",
    "exam": "시험 중간고사 기말고사",
    "assignment_due": "과제 마감 제출",
    "reservation": "예약 예매",
    "departure": "출발 교통",
    "check_in": "체크인 숙박",
    "performance": "공연 콘서트 행사",
    "meeting": "회의 미팅 약속",
    "schedule": "일정 스케줄",
    "none": "",
}


def _join_parts(parts: list[object]) -> str:
    """
    None과 빈 문자열을 제거한 뒤
    검색용 문자열로 합친다.
    """

    return " ".join(
        str(value).strip()
        for value in parts
        if value is not None and str(value).strip()
    )


def build_search_text_v1(event: Event) -> str:
    """
    V1
    현재 방식.

    title + type + date + time + location
    """

    parts = [
        event.title,
        event.type,
        event.date,
        event.time,
        event.location,
    ]

    return _join_parts(parts)


def build_search_text_v2(event: Event) -> str:
    """
    V2
    V1 + end_time + metadata
    """

    parts = [
        event.title,
        event.type,
        event.date,
        event.time,
        event.end_time,
        event.location,
    ]

    if event.metadata is not None:
        metadata = event.metadata.model_dump()

        parts.extend(
            value
            for value in metadata.values()
            if value is not None
        )

    return _join_parts(parts)


def build_search_text_v3(event: Event) -> str:
    """
    V3
    V2에서 내부 event type 대신
    자연어 검색 키워드를 사용한다.
    """

    type_text = EVENT_TYPE_SEARCH_TEXT.get(
        event.type,
        "",
    )

    parts = [
        event.title,
        type_text,
        event.date,
        event.time,
        event.end_time,
        event.location,
    ]

    if event.metadata is not None:
        metadata = event.metadata.model_dump()

        parts.extend(
            value
            for value in metadata.values()
            if value is not None
        )

    return _join_parts(parts)


def build_search_text_v4(
    event: Event,
    caption: str | None,
) -> str:
    """
    V4
    V3 + image caption
    """

    base_text = build_search_text_v3(event)

    return _join_parts(
        [
            base_text,
            caption,
        ]
    )


def build_search_text_v5(
    event: Event,
    caption: str | None,
    ocr_text: str | None,
) -> str:
    """
    V5

    일반 Event:
    - V3 사용

    none Event:
    - OCR + caption 사용
    """

    if event.type == "none":
        return _join_parts(
            [
                ocr_text,
                caption,
            ]
        )

    return build_search_text_v3(event)


def build_search_text_v6(
    event: Event,
    caption: str | None,
    ocr_text: str | None,
) -> str:
    """
    V6

    일반 Event:
    - V3 사용

    none Event:
    - OCR이 있으면 OCR만 사용
    - OCR이 없으면 caption 사용
    """

    if event.type == "none":
        if ocr_text and ocr_text.strip():
            return ocr_text.strip()

        return (caption or "").strip()

    return build_search_text_v3(event)