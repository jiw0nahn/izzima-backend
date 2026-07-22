from typing import Any, Literal

from pydantic import BaseModel, Field


EventType = Literal[
    "expiration",
    "exam",
    "assignment_due",
    "reservation",
    "departure",
    "check_in",
    "performance",
    "meeting",
    "schedule",
    "none",
]


class Event(BaseModel):
    type: EventType = Field(
        description="이미지에서 추출한 이벤트 유형"
    )

    title: str | None = Field(
        default=None,
        description="이벤트 또는 일정의 제목"
    )

    date: str | None = Field(
        default=None,
        description="이벤트 날짜. 가능하면 YYYY-MM-DD 형식"
    )

    time: str | None = Field(
        default=None,
        description="이벤트 시작 시간. 가능하면 HH:MM 형식"
    )

    end_time: str | None = Field(
        default=None,
        description="이벤트 종료 시간. 없으면 null"
    )

    location: str | None = Field(
        default=None,
        description="이벤트 장소"
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="좌석, 예매번호, 금액 등 추가 정보"
    )

    search_text: str = Field(
        default="",
        description="검색에 활용할 핵심 정보를 자연스럽게 합친 문자열"
    )