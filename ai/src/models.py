from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


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


class EventMetadata(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    reservation_number: str | None = None
    order_number: str | None = None
    buyer_name: str | None = None

    purchase_date: str | None = None
    raw_date: str | None = None
    cancellation_deadline: str | None = None

    screen: str | None = None
    seats: list[str] | None = None
    quantity: int | None = None

    amount: int | None = None
    purchase_amount: int | None = None
    ticket_amount: int | None = None

    status: str | None = None
    receive_method: str | None = None
    exchange_code: str | None = None

    category: str | None = None
    format: str | None = None


class Event(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    type: EventType
    title: str | None = None
    date: str | None = None
    time: str | None = None
    end_time: str | None = None
    location: str | None = None

    metadata: EventMetadata = Field(
        default_factory=EventMetadata
    )

    search_text: str = ""