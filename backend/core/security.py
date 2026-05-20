"""
JWT 토큰 생성 및 검증
- python-jose 기반 JWT 처리
- 토큰 만료 시간 설정
"""

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from config import settings


def create_access_token(data: dict) -> str:
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """JWT 액세스 토큰 디코딩"""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
