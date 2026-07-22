import re
from pathlib import Path
from typing import Any

from paddleocr import PaddleOCR


MIN_CONFIDENCE = 0.5


class OCRService:
    def __init__(self) -> None:
        self.ocr = PaddleOCR(
            lang="korean",
            use_doc_orientation_classify=True,
            use_doc_unwarping=True,
            use_textline_orientation=True,
        )

    def _is_valid_text(self, text: str, confidence: float) -> bool:
        """OCR 결과 중 명백하게 불필요한 결과만 제거한다."""

        cleaned_text = text.strip()

        # 빈 문자열 제거
        if not cleaned_text:
            return False

        # 신뢰도가 지나치게 낮은 결과 제거
        if confidence < MIN_CONFIDENCE:
            return False

        # 한글, 영문, 숫자가 하나도 없고 기호만 있는 경우 제거
        if not re.search(r"[가-힣A-Za-z0-9]", cleaned_text):
            return False

        return True

    def extract_text(self, image_path: str | Path) -> dict[str, Any]:
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(f"이미지를 찾을 수 없습니다: {path}")

        results = self.ocr.predict(str(path))

        raw_lines: list[dict[str, Any]] = []
        filtered_lines: list[dict[str, Any]] = []

        for result in results:
            result_json = result.json
            data = result_json.get("res", result_json)

            recognized_texts = data.get("rec_texts", [])
            recognized_scores = data.get("rec_scores", [])

            for index, text in enumerate(recognized_texts):
                confidence = (
                    float(recognized_scores[index])
                    if index < len(recognized_scores)
                    else 0.0
                )

                line = {
                    "text": text.strip(),
                    "confidence": confidence,
                }

                # 원본 OCR 결과는 모두 보관
                raw_lines.append(line)

                # 기본 조건을 통과한 결과만 따로 보관
                if self._is_valid_text(text, confidence):
                    filtered_lines.append(line)

        full_text = "\n".join(
            line["text"] for line in filtered_lines
        )

        return {
            "image_path": str(path),
            "raw_lines": raw_lines,
            "filtered_lines": filtered_lines,
            "full_text": full_text,
        }