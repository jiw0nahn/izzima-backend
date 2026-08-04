"""
app/core/security.py

Supabase Auth가 발급한 JWT를 검증해서 요청자의 user_id(uuid)를 추출하는 의존성.

프론트(React Native)가 supabase-js로 로그인 후 받은 access_token을
`Authorization: Bearer <token>` 헤더로 실어 보내면, 이 모듈이 Supabase 프로젝트의
JWKS(공개키) 엔드포인트로 서명을 검증하고 payload의 `sub` claim(= auth.users.id)을
꺼내 라우트에 전달한다. 서명 검증 없이 decode만 하면 토큰 위조가 가능하므로 반드시
검증을 거친다.

이 프로젝트는 (대시보드에 별도 "JWT Secret"이 없는) 최신 Supabase 비대칭키(ES256)
서명 방식이라, 공유 시크릿 대신 `{SUPABASE_URL}/auth/v1/.well-known/jwks.json`에서
공개키를 받아 검증한다 (PyJWKClient가 캐싱 + kid 매칭을 알아서 처리). algorithms를
["ES256"]으로 고정해서, 토큰 헤더의 alg를 신뢰해 HS256으로 검증하려 드는
algorithm-confusion 공격을 막는다.
"""

import os
from functools import lru_cache

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL이 .env에 설정되어 있지 않습니다.")

_JWKS_URL = f"{SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"

_bearer_scheme = HTTPBearer(auto_error=False)


@lru_cache
def _get_jwk_client() -> PyJWKClient:
    return PyJWKClient(_JWKS_URL)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> str:
    """요청 헤더의 Bearer 토큰을 검증하고 user_id(uuid 문자열)를 반환한다."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 토큰이 필요합니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        signing_key = _get_jwk_client().get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
        )
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"유효하지 않은 토큰입니다: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰에 sub claim이 없습니다.",
        )

    return user_id
