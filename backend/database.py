"""
QMS 데이터베이스 설정
- SQLAlchemy 엔진 및 세션 팩토리
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

# PostgreSQL 엔진 생성 (커넥션 풀링 설정)
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=1800,
)

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
