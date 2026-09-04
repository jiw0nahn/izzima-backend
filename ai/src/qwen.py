import json
import os
from typing import Literal

from ollama import chat
from pydantic import BaseModel, ValidationError

from models import Event
from postprocess import postprocess_event


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

    def classify_event_type(
        self,
        ocr_text: str,
        caption: str | None = None,
    ) -> EventType:
        """
        OCR 텍스트와 BLIP 이미지 캡션을 기반으로
        이벤트 유형을 분류한다.
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
   - 날짜, 시간, 장소, 상품명 등
     정확한 문자 정보의 주 근거다.

2. 이미지 캡션
   - 이미지의 종류와 전체적인 맥락을 판단하는 보조 정보다.

OCR 텍스트와 이미지 캡션이 충돌하면 OCR 텍스트를 우선한다.

이미지 캡션만으로 날짜, 시간, 장소, 금액 등의
구체적인 값을 추측하지 않는다.

OCR에는 일부 잘못 인식된 문자열이 포함될 수 있다.
하지만 정상적으로 의미를 파악할 수 있는 상품명, 날짜, 장소,
이벤트 관련 키워드까지 OCR 오류라고 간주하여 무시하지 않는다.

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
  콘서트, 페스티벌, 공연, 전시회,
  스포츠 경기 등 관람 행사

- meeting:
  회의, 상담, 면담, 미팅

- schedule:
  위 유형에 속하지 않는 일반 일정

- none:
  일정이나 관리할 이벤트 정보를 찾을 수 없음

중요 규칙:

1. 공연 예매 내역이어도 실제 핵심 이벤트가
   콘서트나 페스티벌이면 performance다.

2. 영화 예매는 reservation이다.

3. 상품권, 쿠폰, 이용권과 함께
   "유효기간", "사용기한", "만료일"이 확인되면 expiration이다.

4. 버튼명, 결제 상태, 상태바, 일반 안내 문구는
   핵심 분류 근거에서 제외한다.

5. 이미지 캡션은 OCR에서 부족한
   이미지 종류와 전체 맥락만 보완한다.

6. OCR에서 이벤트를 나타내는 명확한 핵심 단서가 존재하면
   해당 이벤트 유형을 적극적으로 선택한다.

7. none은 날짜, 예약, 일정, 만료, 시험, 공연 등
   사용자가 관리할 이벤트를 나타내는 근거가
   전혀 없는 경우에만 선택한다.

8. JSON 객체 하나만 출력한다.
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
        분류된 이벤트 유형을 기반으로
        구조화된 이벤트 정보를 추출한다.
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

OCR 텍스트와 이미지 캡션이 충돌하면
OCR 텍스트를 우선한다.

이미지 캡션만으로 OCR에 없는 날짜, 시간,
장소, 금액 등의 값을 새롭게 만들어내지 않는다.

필드 추출 기본 원칙:

- OCR에서 의미가 명확하게 확인되는 정보는 적극적으로 추출한다.

- 필드 라벨과 값의 관계가 명확하면 해당 값을 사용한다.

예:

"유효기간"
"2022년 7월 16일"

→ date = "2022-07-16"

"교환처"
"GS25"

→ location = "GS25"

"모바일 상품권 5만원권"

→ title = "모바일 상품권 5만원권"

- 명확한 근거가 없는 정보만 null로 작성한다.

- 정상적인 상품명, 장소명, 날짜, 시간, 금액 등을
  OCR 노이즈라고 판단하여 무시하지 않는다.

- OCR에는 일부 깨진 문자열이나 잘못 인식된 텍스트가
  포함될 수 있다.

- 다른 문맥이나 필드와 연결되지 않는
  의미 없는 문자열만 무시한다.

- 동일한 OCR 값을 의미 없이
  여러 metadata 필드에 중복 저장하지 않는다.

- metadata에는 해당 이벤트에 실제 필요한 정보만 저장한다.

- 버튼명, 안내문, 결제 버튼, 상태바 텍스트는 무시한다.


날짜 처리 규칙:

- 연도, 월, 일이 모두 존재하면
  반드시 YYYY-MM-DD 형식으로 변환한다.

예:

"2022년 7월 16일"

→ date = "2022-07-16"
→ metadata.raw_date = null

"2025.07.05(토)"

→ date = "2025-07-05"
→ metadata.raw_date = null

- 핵심 이벤트 날짜에 연도가 직접 표시되지 않은 경우
  근거 없이 연도를 추측해서 넣지 않는다.

- 현재 연도, 시스템 날짜, 일반적인 관행만으로
  누락된 연도를 보완하지 않는다.

예:

"상영일"
"11.07"

→ date = null
→ metadata.raw_date = "11.07"

"11/26"

→ date = null
→ metadata.raw_date = "11/26"

- 단, OCR의 다른 위치에
  해당 월/일과 명확하게 대응되는 연도 정보가 존재하면
  그 연도를 사용할 수 있다.

예:

"판매번호"
"2026-0307-5348-0221"

"상영일"
"03/07"

→ 두 정보가 동일한 03/07을 명확하게 가리키는 경우
   date = "2026-03-07"
   metadata.raw_date = null

- 서로 관련이 없는 숫자나 문자열의 연도를
  날짜에 억지로 결합하지 않는다.

- YYYY-MM-DD로 정상 변환할 수 있는 날짜를
  metadata.raw_date에 저장하지 않는다.


시간 처리 규칙:

- 시간은 HH:MM 형식으로 작성한다.

예:

"19:55"
→ time = "19:55"

"2025.07.05(토)13:00"
→ date = "2025-07-05"
→ time = "13:00"

- 종료 시간이 명시되어 있으면 end_time에 저장한다.

예:

"19:45"
"~21:30"

→ time = "19:45"
→ end_time = "21:30"


금액 처리 규칙:

- OCR에 금액이 명확하게 표시되어 있으면 적극적으로 추출한다.

- 쉼표와 통화 단위는 제거하고 정수로 저장한다.

예:

"50,000원"
→ 50000

"5만원"
→ 50000

"10,000"
→ 10000

- 상품권, 쿠폰, 이용권 자체의 표시 금액은
  metadata.amount에 저장한다.

- 사용자가 실제 결제한 금액은
  metadata.purchase_amount에 저장한다.

- 영화, 공연, 교통 등 티켓 자체의 가격은
  metadata.ticket_amount에 저장한다.

예:

"구매금액"
"145,000원"

→ metadata.purchase_amount = 145000

"티켓금액"
"143,000원"

→ metadata.ticket_amount = 143000


metadata 키 정의:

- reservation_number:
  예약 또는 예매 번호

  "예매번호", "예약번호", "판매번호" 등
  예약이나 예매를 식별하는 번호를 저장한다.

- order_number:
  상품 주문 번호

  "주문번호" 라벨에 해당하는 값을 저장한다.

- buyer_name:
  구매자, 주문자 또는 예매자 이름

  "구매자", "주문자", "예매자", "예매자명",
  "받는 분", "보낸 사람" 등
  사람 이름임을 나타내는 명확한 라벨이 있을 때 추출한다.

  단독으로 등장하는 사람 이름처럼 보이는 문자열은
  buyer_name으로 추측하지 않는다.

- purchase_date:
  상품, 티켓, 예약을 구매하거나 예매한 날짜

  "구매일", "결제일", "예매일" 등
  구매 또는 예매 시점을 나타내는 날짜를 저장한다.

  실제 관람일, 공연일, 상영일과 혼동하지 않는다.

- raw_date:
  연도 누락 등으로 YYYY-MM-DD 형식으로
  정상 변환할 수 없는 핵심 이벤트 날짜의 원문

- cancellation_deadline:
  취소 또는 환불 가능 마감 일시

  "취소마감", "취소마감일", "취소마감일시",
  "환불마감" 등의 라벨이 있으면 적극적으로 추출한다.

- screen:
  영화관의 상영관 번호 또는 상영관명

- seats:
  실제 좌석 번호 또는 좌석명

  "H7", "G6", "113", "A열 5번"처럼
  실제 좌석을 나타내는 값만 저장한다.

  "일반 1명", "성인 1명", "청소년 2명",
  "일반1", "성인1" 등은 인원 정보이며
  seats에 저장하지 않는다.

- quantity:
  매수 또는 인원수

  "1매", "2매", "성인 1명", "일반 1명",
  "청소년 2명", "일반1", "성인1" 등에서
  수량만 정수로 저장한다.

- amount:
  쿠폰, 상품권, 이용권 등에 명시된 금액 또는 권면가

  반드시 OCR에 금액을 나타내는 명확한 근거가 있을 때만 추출한다.

  금액으로 인정할 수 있는 예:
  - 50,000원
  - 5만원
  - 5만원권
  - 금액 10,000원

  다음 숫자는 절대 금액으로 해석하지 않는다:
  - 제품 중량: 54g, 100g
  - 열량: 270 kcal
  - 용량: 500ml
  - 개수
  - 바코드 번호
  - 주문번호
  - 예약번호
  - 날짜
  - OCR에 단순히 등장하는 숫자

  "원", "만원", "천원", "원권" 등
  화폐 단위나 금액을 의미하는 명확한 표현이 없다면
  amount는 null로 반환한다.

예:

"모바일 상품권 5만원권"
→ amount = 50000

"오리지날 54 g (270 kcal)"
→ amount = null

- purchase_amount:
  사용자가 실제 결제한 총 금액

  "구매금액", "결제금액", "총 결제금액" 등
  실제 결제 금액임을 나타내는 라벨이 있으면 추출한다.

- ticket_amount:
  영화, 공연, 교통 등 티켓 자체의 금액

  "티켓금액", "티켓가격" 등의 값을 저장한다.

- status:
  예약, 주문, 티켓 등의 현재 상태

  "상태", "예매상태", "주문상태" 등의
  명확한 상태 라벨에 직접 연결된 값만 저장한다.

  "예매취소", "예약취소", "취소하기",
  "좌석보기", "선물하기"처럼
  사용자가 누르는 버튼이나 메뉴 텍스트는
  현재 상태가 아니므로 저장하지 않는다.

예:

"상태"
"예매완료(입금완료)"

→ status = "예매완료(입금완료)"

"예매취소"
"좌석보기"

→ status = null

- receive_method:
  티켓 또는 상품 수령 방법

  "수령방법", "티켓수령 방법" 등의 값을 저장한다.

- exchange_code:
  쿠폰 또는 상품권의 교환 코드 또는 바코드 번호

- category:
  이벤트의 의미가 명확할 때만
  추가 카테고리 정보를 저장한다.

  OCR 오류로 보이는 문자열이나
  단순 브랜드 문구를 억지로 category로 만들지 않는다.

- format:
  상품권 또는 티켓의 형태

  "모바일", "지류", "e-ticket", "QR 티켓", "2D" 등
  실제 형식이나 티켓 형태를 나타내는 의미가
  입력에서 명확하게 확인되는 경우에만 저장한다.

  의미를 해석할 수 없는 OCR 문자열은 저장하지 않는다.

예:

"S5ES"
"25ES"
"GIAMSS"

→ format = null


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
  OCR에 명확하게 존재하면 다음 정보를 추출한다.

  reservation_number
  buyer_name
  purchase_date
  cancellation_deadline
  seats
  quantity
  purchase_amount
  ticket_amount
  status
  receive_method
  category
  format


reservation:

- title:
  영화명, 병원명, 식당명, 숙소명 등 실제 예약 대상

  서비스 이름이나 UI 헤더보다
  실제 예약 대상을 우선한다.

  실제 예약 대상명이 OCR에 없다면
  "MEGABOX TICKET", "모바일 티켓", "예매내역"처럼
  서비스명이나 일반적인 티켓 문구를
  억지로 title로 사용하지 않는다.

- date/time:
  실제 예약 또는 관람 날짜와 시간

- end_time:
  종료 시간이 명시되어 있으면 저장한다.

- location:
  극장, 병원, 식당, 숙소 등
  실제 예약이 이루어지는 장소

- metadata:
  OCR에 명확하게 존재하면 다음 정보를 추출한다.

  reservation_number
  buyer_name
  purchase_date
  cancellation_deadline
  screen
  seats
  quantity
  purchase_amount
  ticket_amount
  status
  receive_method
  category
  format


expiration:

- title:
  상품권, 쿠폰, 이용권의 이름

- date:
  "유효기간", "사용기한", "만료일"에 해당하는 날짜

- location:
  "교환처", "사용처"에 해당하는 장소 또는 브랜드

- metadata.order_number:
  "주문번호"에 해당하는 값

- metadata.exchange_code:
  교환 코드 또는 바코드 번호

- metadata.amount:
  상품권 또는 쿠폰 자체의 표시 금액

금액 예:

"50,000원"
→ metadata.amount = 50000

"5만원"
→ metadata.amount = 50000

- 상품권 자체의 금액에는 amount를 사용한다.
- ticket_amount는 사용하지 않는다.

- "모바일 상품권", "모바일 쿠폰"처럼
  상품권의 형태가 명확한 경우
  metadata.format = "모바일"로 저장할 수 있다.


exam:

- title:
  시험명 또는 과목명

- date/time:
  시험 일시

- location:
  시험 장소 또는 강의실

- metadata:
  OCR에 명확하게 존재하는 정보만 저장한다.


assignment_due:

- title:
  과제명, 보고서명, 프로젝트명

- date/time:
  제출 마감 일시

- location:
  제출 위치가 명시된 경우에만 저장한다.

- metadata:
  OCR에 명확하게 존재하는 정보만 저장한다.


departure:

- title:
  항공편, 기차, 버스 등 이동 일정명

- date/time:
  출발 일시

- location:
  출발 장소

- metadata:
  reservation_number 등
  OCR에서 명확하게 확인되는 정보만 저장한다.


check_in:

- title:
  숙소명 또는 항공편명

- date/time:
  체크인 일시

- location:
  숙소 또는 공항

- metadata:
  reservation_number 등
  OCR에서 명확하게 확인되는 정보만 저장한다.


meeting:

- title:
  회의명, 상담명, 면담명

- date/time:
  회의 일시

- location:
  회의 장소

- metadata:
  OCR에 명확하게 존재하는 정보만 저장한다.


schedule:

- title:
  일반 일정명

- date/time:
  일정 일시

- location:
  일정 장소

- metadata:
  OCR에 명확하게 존재하는 정보만 저장한다.


none:

- 일정이나 이벤트가 없는 경우다.
- title, date, time, end_time, location은 null로 작성한다.
- metadata에는 이벤트와 관련 없는 정보를 저장하지 않는다.


중요:

- search_text는 모델이 작성할 필요가 없다.
- search_text는 프로그램에서 별도로 생성한다.
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

        # 분류 단계에서 결정한 type은 변경하지 못하도록 강제한다.
        parsed_data["type"] = event_type

        metadata = parsed_data.get("metadata")

        if not isinstance(metadata, dict):
            parsed_data["metadata"] = {}

        # search_text는 LLM에게 맡기지 않고
        # postprocess 단계에서 직접 만든다.
        parsed_data["search_text"] = ""

        try:
            event = Event.model_validate(parsed_data)
        except ValidationError as error:
            raise ValueError(
                "Qwen 응답이 Event 스키마와 일치하지 않습니다.\n"
                f"원본 응답:\n{raw_content}\n\n"
                f"검증 오류:\n{error}"
            ) from error

        return postprocess_event(
            event=event,
            ocr_text=ocr_text,
        )

    def process(
        self,
        ocr_text: str,
        caption: str | None = None,
    ) -> Event:
        """
        이벤트 유형 분류 후
        구조화 정보 추출까지 순서대로 실행한다.
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