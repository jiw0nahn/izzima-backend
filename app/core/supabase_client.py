"""
app/core/supabase_client.py

Supabase client 싱글톤.
SUPABASE_URL은 반드시 base project URL만 사용 (예: https://xxxx.supabase.co)
'/rest/v1' 같은 경로를 붙이면 PGRST125 에러 발생하므로 주의.
"""

import os
from functools import lru_cache

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL / SUPABASE_KEY가 .env에 설정되어 있지 않습니다."
    )


@lru_cache
def get_supabase_client() -> Client:
    """
    FastAPI 요청마다 새로 만들지 않도록 캐싱된 client를 반환.
    반드시 service_role key를 사용해야 함 (RLS 우회, 서버 사이드 전용).
    anon key를 쓰면 테이블/버킷 정책이 없는 한 insert/upload가 42501로 막힘.
    """
    return create_client(SUPABASE_URL, SUPABASE_KEY)