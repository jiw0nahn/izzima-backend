from models import Event
from postprocess.extractors import extract_amount_from_ocr
from postprocess.search_text import (
    build_search_text_v1,
    build_search_text_v2,
    build_search_text_v3,
    build_search_text_v4,
)


def postprocess_event(
    event: Event,
    ocr_text: str,
    caption: str | None = None,
    search_text_version: int = 1,
) -> Event:

    # 1. 규칙 기반 Event 보완
    metadata = event.metadata.model_dump()

    if event.type == "expiration":
        metadata["amount"] = extract_amount_from_ocr(
            ocr_text
        )

    updated_event = event.model_copy(
        update={
            "metadata": event.metadata.model_copy(
                update=metadata,
            ),
        }
    )

    # 2. search_text 생성
    if search_text_version == 1:
        search_text = build_search_text_v1(updated_event)

    elif search_text_version == 2:
        search_text = build_search_text_v2(updated_event)

    elif search_text_version == 3:
        search_text = build_search_text_v3(updated_event)

    elif search_text_version == 4:
        search_text = build_search_text_v4(
            updated_event,
            caption,
        )

    else:
        raise ValueError(
            f"Unsupported search_text_version: {search_text_version}"
        )

    # 3. 최종 Event 생성
    return updated_event.model_copy(
        update={"search_text": search_text}
    )