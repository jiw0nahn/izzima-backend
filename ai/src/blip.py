from __future__ import annotations

from io import BytesIO

import torch
from PIL import Image, UnidentifiedImageError
from transformers import BlipForConditionalGeneration, BlipProcessor


MODEL_NAME = "Salesforce/blip-image-captioning-base"


def _get_device() -> torch.device:
    """사용 가능한 연산 장치를 선택한다."""
    if torch.backends.mps.is_available():
        return torch.device("mps")

    if torch.cuda.is_available():
        return torch.device("cuda")

    return torch.device("cpu")


DEVICE = _get_device()

# 모델은 함수 호출마다 다시 로드하지 않고 모듈 로딩 시 한 번만 불러온다.
PROCESSOR = BlipProcessor.from_pretrained(MODEL_NAME)
MODEL = BlipForConditionalGeneration.from_pretrained(MODEL_NAME)
MODEL.to(DEVICE)
MODEL.eval()


def _load_image(image_bytes: bytes) -> Image.Image:
    """이미지 bytes를 BLIP 입력용 RGB 이미지로 변환한다."""
    if not image_bytes:
        raise ValueError("image_bytes가 비어 있습니다.")

    try:
        image = Image.open(BytesIO(image_bytes))
        return image.convert("RGB")
    except UnidentifiedImageError as error:
        raise ValueError("유효한 이미지 파일이 아닙니다.") from error


def generate_caption(
    image_bytes: bytes,
    max_new_tokens: int = 40,
) -> str:
    """
    이미지 bytes를 받아 영어 이미지 캡션을 생성한다.

    BLIP 기본 체크포인트는 주로 영어 캡션을 생성하므로,
    이후 Qwen에 OCR 텍스트와 함께 전달해 한국어 search_text와
    구조화 정보를 생성하는 방식으로 사용한다.
    """
    image = _load_image(image_bytes)

    inputs = PROCESSOR(
        images=image,
        return_tensors="pt",
    )

    inputs = {
        key: value.to(DEVICE)
        for key, value in inputs.items()
    }

    with torch.inference_mode():
        output_ids = MODEL.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            num_beams=3,
        )

    caption = PROCESSOR.decode(
        output_ids[0],
        skip_special_tokens=True,
    )

    return caption.strip()