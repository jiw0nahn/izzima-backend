import re


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

    won_match = re.search(
        r"(\d{1,3}(?:,\d{3})+|\d+)\s*원",
        ocr_text,
    )

    if won_match:
        return int(
            won_match.group(1).replace(",", "")
        )

    return None