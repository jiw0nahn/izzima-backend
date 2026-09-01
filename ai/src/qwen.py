import json
import os

from typing import Literal

from ollama import chat
from pydantic import BaseModel, ValidationError

from models import Event


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


class ClassificationResult(BaseModel):
    type: EventType


class QwenService:
    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or os.getenv(
            "OLLAMA_MODEL",
            "qwen3.5:9b",
        )

    @staticmethod
    def _build_input_context(
        ocr_text: str,
        caption: str | None,
    ) -> str:
        """
        OCR 텍스트와 BLIP 이미지 캡션을 하나의 입력 문맥으로 구성한다.

        OCR은 날짜, 시간, 장소 등 정확한 문자 정보의 주 근거로 사용하고,
        BLIP 캡션은 이미지 종류와 전체 맥락을 판단하는 보조 정보로 사용한다.
        """

        normalized_ocr_text = ocr_text.strip() if ocr_text else ""
        normalized_caption = caption.strip() if caption else ""

        return f"""
OCR 텍스트:
{normalized_ocr_text or "없음"}

이미지 캡션:
{normalized_caption or "없음"}
""".strip()

    @staticmethod
    def _build_search_text(event: Event) -> str:
        """
        구조화된 Event 데이터를 기반으로 검색용 텍스트를 생성한다.

        주문번호, 교환코드, 예매번호 등 식별 정보는 검색 텍스트에 넣지 않는다.
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

    def classify_event_type(
        self,
        ocr_text: str,
        caption: str | None = None,
    ) -> EventType:
        """
        OCR 텍스트와 BLIP 이미지 캡션을 바탕으로 이벤트 유형을 분류한다.
        """

        input_context = self._build_input_context(
            ocr_text=ocr_text,
            caption=caption,
        )

        response = chat(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": """
너는 이미지에서 추출된 OCR 텍스트와 이미지 캡션을 보고
사용자가 기억하거나 관리해야 할 핵심 이벤트 유형을 분류하는 시스템이다.

정보 출처 우선순위:

1. OCR 텍스트
   - 날짜, 시간, 장소, 상품명 등 정확한 문자 정보의 주 근거다.

2. 이미지 캡션
   - 이미지 전체의 맥락과 문서 종류를 판단하기 위한 보조 정보다.

OCR 텍스트와 이미지 캡션이 충돌하면 OCR 텍스트를 우선한다.

이미지 캡션만으로 날짜, 시간, 장소, 금액 등의
구체적인 정보를 추측하지 않는다.

OCR에는 잘못 인식된 문자열이나 의미 없는 문자 조각이 포함될 수 있다.
문맥적 근거가 없는 깨진 문자열은 분류 근거로 사용하지 않는다.

문서의 표면 형식이 아니라
사용자가 기억하거나 관리해야 할 핵심 이벤트를 기준으로 분류한다.

유형 정의:

- expiration:
  쿠폰, 상품권, 포인트, 이용권의 유효기간 또는 만료일

- exam:
  학교 시험, 중간고사, 기말고사, 자격시험

- assignment_due:
  과제, 보고서, 프로젝트 제출 마감

- reservation:
  영화, 식당, 병원, 숙소 등의 예약 또는 예매 일정

- departure:
  항공기, 기차, 버스 등의 출발 일정

- check_in:
  숙소 또는 항공편의 체크인 일정

- performance:
  콘서트, 페스티벌, 공연, 전시회, 스포츠 경기 등 관람 행사

- meeting:
  회의, 상담, 면담, 미팅

- schedule:
  위 유형에 속하지 않는 일반 일정

- none:
  일정이나 이벤트 정보를 찾을 수 없음

중요 규칙:

1. 공연 예매 내역이어도 실제 핵심 이벤트가
   콘서트나 페스티벌이면 performance다.

2. 영화 예매는 reservation이다.

3. 상품권의 핵심 날짜가 유효기간이면 expiration이다.

4. 버튼명, 결제 상태, 상태바, 안내 문구는
   이벤트 유형 판단의 핵심 근거로 사용하지 않는다.

5. 이미지 캡션은 OCR에서 부족한
   이미지 종류와 전체 맥락만 보완한다.

6. 명확한 근거가 없으면 none을 선택한다.

7. JSON 객체 하나만 출력한다.
""".strip(),
                },

                # Few-shot 1: 공연
                {
                    "role": "user",
                    "content": """
OCR 텍스트:
WATERBOMB
관람일
2025.07.05(토)13:00
공연장소
일산 킨텍스 제2전시장

이미지 캡션:
a mobile ticket for a music festival
""".strip(),
                },
                {
                    "role": "assistant",
                    "content": json.dumps(
                        {"type": "performance"},
                        ensure_ascii=False,
                    ),
                },

                # Few-shot 2: 영화 예매
                {
                    "role": "user",
                    "content": """
OCR 텍스트:
주토피아 2(자막)
11/26
19:55
서면삼정타워
8관
G6
G7

이미지 캡션:
a screenshot of a movie ticket reservation
""".strip(),
                },
                {
                    "role": "assistant",
                    "content": json.dumps(
                        {"type": "reservation"},
                        ensure_ascii=False,
                    ),
                },

                # Few-shot 3: 상품권 만료
                {
                    "role": "user",
                    "content": """
OCR 텍스트:
GS25
모바일 상품권 5만원권
유효기간
2026년 7월 16일

이미지 캡션:
a mobile gift card coupon
""".strip(),
                },
                {
                    "role": "assistant",
                    "content": json.dumps(
                        {"type": "expiration"},
                        ensure_ascii=False,
                    ),
                },

                # 실제 입력
                {
                    "role": "user",
                    "content": input_context,
                },
            ],
            format=ClassificationResult.model_json_schema(),
            think=False,
            options={
                "temperature": 0,
                "seed": 42,
            },
        )

        raw_content = response.message.content.strip()

        if not raw_content:
            raise ValueError("Qwen 분류 응답이 비어 있습니다.")

        try:
            parsed_data = json.loads(raw_content)
        except json.JSONDecodeError as error:
            raise ValueError(
                "Qwen 분류 응답을 JSON으로 변환할 수 없습니다.\n"
                f"원본 응답:\n{raw_content}"
            ) from error

        try:
            result = ClassificationResult.model_validate(parsed_data)
        except ValidationError as error:
            raise ValueError(
                "Qwen 분류 응답이 ClassificationResult 스키마와 "
                "일치하지 않습니다.\n"
                f"원본 응답:\n{raw_content}\n\n"
                f"검증 오류:\n{error}"
            ) from error

        return result.type

    def extract_event(
        self,
        ocr_text: str,
        event_type: EventType,
        caption: str | None = None,
    ) -> Event:
        """
        분류된 이벤트 유형을 바탕으로 구조화된 이벤트 정보를 추출한다.
        """

        input_context = self._build_input_context(
            ocr_text=ocr_text,
            caption=caption,
        )

        response = chat(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": f"""
너는 이미지에서 추출된 OCR 텍스트와 이미지 캡션을 보고
구조화된 이벤트 정보를 추출하는 시스템이다.

이미 분류된 이벤트 유형은 "{event_type}"이다.
이 유형을 임의로 변경하지 않는다.

정보 출처 우선순위:

1. OCR 텍스트
   - 날짜, 시간, 장소, 제목, 좌석, 금액 등의
     정확한 문자 정보의 주 근거다.

2. 이미지 캡션
   - 이미지의 종류와 전체적인 시각적 맥락을 판단하는
     보조 정보다.
   - OCR에 명시되지 않은 날짜, 시간, 장소, 금액 등의
     구체적인 정보를 캡션만 보고 추측하지 않는다.

OCR 텍스트와 이미지 캡션이 충돌하면 OCR 텍스트를 우선한다.

필드 추출 원칙:

- 각 필드는 반드시 입력에서 근거를 확인할 수 있어야 한다.
- 명확한 근거가 없으면 null로 작성한다.
- OCR에는 잘못 인식된 문자열이 포함될 수 있다.
- 문맥적 근거가 없는 깨진 문자열은
  이름, 장소, 제목 등의 값으로 사용하지 않는다.
- 동일한 OCR 값을 의미 없이 여러 metadata 필드에 중복 저장하지 않는다.
- metadata에는 해당 이벤트에 실제로 필요한 정보만 저장한다.
- 버튼명, 안내문, 결제 버튼, 상태바 텍스트는 무시한다.
- OCR 인식 오류로 보이는 문구를 임의로 수정하거나 추측하지 않는다.

날짜 및 시간 규칙:

- 날짜는 YYYY-MM-DD 형식으로 작성한다.
- 시간은 HH:MM 형식으로 작성한다.

예:
"2025.07.05(토)13:00"

→
date = "2025-07-05"
time = "13:00"

연도가 없는 날짜:

예:
"11/26"

→
date = null
metadata.raw_date = "11/26"

metadata 키 정의:

- reservation_number:
  예약 또는 예매 번호

- order_number:
  상품 주문 번호

- buyer_name:
  구매자 또는 주문자 이름
  "구매자", "주문자", "받는 분" 등
  이름을 나타내는 명확한 문맥이 있을 때만 사용한다.

- purchase_date:
  상품이나 티켓을 실제 구매한 날짜

- raw_date:
  연도 누락 등으로 표준 날짜 형식으로 변환할 수 없는 날짜 원문

- screen:
  영화관의 상영관 번호 또는 상영관명

- seats:
  좌석 정보

- quantity:
  매수 또는 수량

- amount:
  쿠폰, 상품권, 이용권 자체의 표시 금액 또는 가치

- purchase_amount:
  사용자가 실제 결제한 금액

- ticket_amount:
  영화, 공연, 교통 등 티켓의 가격

- cancellation_deadline:
  취소 또는 환불 가능 마감 시각

- status:
  예약, 주문, 티켓 등의 상태

- receive_method:
  티켓 또는 상품 수령 방법

- exchange_code:
  쿠폰 또는 상품권 교환 코드

- category:
  문서나 이벤트의 추가 카테고리

- format:
  상품권 또는 티켓의 형태

metadata에는 위에서 정의한 키만 사용한다.

유형별 추출 기준:

performance:

- title:
  공연명, 콘서트명, 페스티벌명

- date/time:
  관람일 또는 공연일

- location:
  공연장소

- metadata:
  reservation_number
  quantity
  ticket_amount
  receive_method

reservation:

- title:
  영화명, 병원명, 식당명, 숙소명 등 예약 대상

- date/time:
  예약 또는 관람 날짜와 시간

- end_time:
  종료 시간이 명시된 경우 저장

- location:
  극장, 병원, 식당, 숙소

- metadata:
  reservation_number
  screen
  seats
  ticket_amount

expiration:

- title:
  상품권, 쿠폰, 이용권 이름

- date:
  유효기간 또는 만료일

- location:
  교환처 또는 사용처

- metadata:
  order_number
  exchange_code
  amount

- 상품권 또는 쿠폰의 표시 금액은 amount를 사용한다.
- ticket_amount는 사용하지 않는다.

exam:

- title:
  시험명 또는 과목명

- date/time:
  시험 일시

- location:
  시험 장소 또는 강의실

assignment_due:

- title:
  과제명, 보고서명, 프로젝트명

- date/time:
  제출 마감 일시

- location:
  제출 위치가 명시된 경우만 저장

departure:

- title:
  항공편, 기차, 버스 등 이동 일정명

- date/time:
  출발 일시

- location:
  출발 장소

- metadata:
  reservation_number 등 명확하게 확인되는 정보만 저장

check_in:

- title:
  숙소명 또는 항공편명

- date/time:
  체크인 일시

- location:
  숙소 또는 공항

- metadata:
  reservation_number 등 명확하게 확인되는 정보만 저장

meeting:

- title:
  회의명, 상담명, 면담명

- date/time:
  회의 일시

- location:
  회의 장소

schedule:

- title:
  일반 일정명

- date/time:
  일정 일시

- location:
  일정 장소

none:

- 일정이나 이벤트가 없으므로 알 수 없는 필드는 null로 작성한다.
- metadata는 빈 객체로 작성한다.

중요:

- search_text는 생성하지 않아도 된다.
- search_text는 이후 프로그램에서 별도로 생성한다.
- JSON 객체 하나만 출력한다.
""".strip(),
                },
                {
                    "role": "user",
                    "content": f"""
이벤트 유형:
{event_type}

{input_context}
""".strip(),
                },
            ],
            format=Event.model_json_schema(),
            think=False,
            options={
                "temperature": 0,
                "seed": 42,
            },
        )

        raw_content = response.message.content.strip()

        if not raw_content:
            raise ValueError("Qwen 추출 응답이 비어 있습니다.")

        try:
            parsed_data = json.loads(raw_content)
        except json.JSONDecodeError as error:
            raise ValueError(
                "Qwen 응답을 JSON으로 변환할 수 없습니다.\n"
                f"원본 응답:\n{raw_content}"
            ) from error

        # 분류 단계에서 결정한 이벤트 유형을 강제로 유지한다.
        parsed_data["type"] = event_type

        metadata = parsed_data.get("metadata")

        if not isinstance(metadata, dict):
            parsed_data["metadata"] = {}

        # LLM이 생성한 search_text는 사용하지 않는다.
        # Event validation을 위해 임시값을 넣는다.
        parsed_data["search_text"] = ""

        try:
            event = Event.model_validate(parsed_data)
        except ValidationError as error:
            raise ValueError(
                "Qwen 응답이 Event 스키마와 일치하지 않습니다.\n"
                f"원본 응답:\n{raw_content}\n\n"
                f"검증 오류:\n{error}"
            ) from error

        # 구조화된 필드를 기반으로 search_text를 결정론적으로 생성한다.
        event.search_text = self._build_search_text(event)

        return event

    def process(
        self,
        ocr_text: str,
        caption: str | None = None,
    ) -> Event:
        """
        이벤트 유형 분류 후 구조화 정보 추출까지 순서대로 실행한다.
        """

        event_type = self.classify_event_type(
            ocr_text=ocr_text,
            caption=caption,
        )

        return self.extract_event(
            ocr_text=ocr_text,
            caption=caption,
            event_type=event_type,
        )