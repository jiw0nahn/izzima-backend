import re
from typing import Any

import cv2
import numpy as np
from numpy.typing import NDArray
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

    @staticmethod
    def _decode_image(image_bytes: bytes) -> NDArray[np.uint8]:
        """
        이미지 바이트를 PaddleOCR이 처리할 수 있는
        OpenCV 이미지 배열로 변환한다.
        """
        if not image_bytes:
            raise ValueError("이미지 바이트가 비어 있습니다.")

        byte_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8,
        )

        image = cv2.imdecode(
            byte_array,
            cv2.IMREAD_COLOR,
        )

        if image is None:
            raise ValueError(
                "이미지 바이트를 디코딩할 수 없습니다. "
                "지원되는 이미지 형식인지 확인해주세요."
            )

        return image

    @staticmethod
    def _is_valid_text(
        text: str,
        confidence: float,
    ) -> bool:
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

    def extract_text(
        self,
        image_bytes: bytes,
    ) -> dict[str, Any]:
        """
        이미지 바이트를 받아 OCR을 수행하고,
        원본 및 필터링된 텍스트 결과를 반환한다.
        """
        image = self._decode_image(image_bytes)

        results = self.ocr.predict(image)

        raw_lines: list[dict[str, Any]] = []
        filtered_lines: list[dict[str, Any]] = []

        for result in results:
            result_json = result.json
            data = result_json.get("res", result_json)

            recognized_texts = data.get("rec_texts", [])
            recognized_scores = data.get("rec_scores", [])

            for index, text in enumerate(recognized_texts):
                normalized_text = str(text).strip()

                confidence = (
                    float(recognized_scores[index])
                    if index < len(recognized_scores)
                    else 0.0
                )

                line = {
                    "text": normalized_text,
                    "confidence": confidence,
                }

                # 원본 OCR 결과는 모두 보관
                raw_lines.append(line)

                # 기본 조건을 통과한 결과만 따로 보관
                if self._is_valid_text(
                    normalized_text,
                    confidence,
                ):
                    filtered_lines.append(line)

        full_text = "\n".join(
            line["text"]
            for line in filtered_lines
        )

        return {
            "raw_lines": raw_lines,
            "filtered_lines": filtered_lines,
            "full_text": full_text,
        }