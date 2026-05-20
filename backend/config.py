"""
QMS 애플리케이션 설정
- pydantic-settings 기반 환경변수 관리
- DATABASE_URL, JWT 설정 등
"""

import secrets
import warnings
from pydantic_settings import BaseSettings

# 고정된 기본 시크릿 사용을 방지하기 위해 매 실행마다 랜덤 키 생성
_DEFAULT_SECRET_KEY = secrets.token_hex(32)


class Settings(BaseSettings):
    """애플리케이션 설정 (환경변수 / .env 파일에서 로드)"""

    # 데이터베이스
    DATABASE_URL: str = "postgresql://ybr@localhost:5432/mes_db"

    # JWT 인증
    SECRET_KEY: str = _DEFAULT_SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8시간

    # 페이지네이션 기본값
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    MASTER_PAGE_SIZE: int = 50
    MASTER_MAX_PAGE_SIZE: int = 200

    # 앱 정보
    APP_NAME: str = "QMS API"
    APP_VERSION: str = "1.0.0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# SECRET_KEY가 환경변수로 설정되지 않은 경우 경고
if settings.SECRET_KEY == _DEFAULT_SECRET_KEY:
    warnings.warn(
        "SECRET_KEY가 설정되지 않아 임시 랜덤 키를 사용합니다. "
        "서버 재시작 시 기존 토큰이 무효화됩니다. "
        ".env 파일에 SECRET_KEY를 설정하세요.",
        stacklevel=1,
    )
