"""
ORM 베이스 클래스 정의
- ExistingBase: 기존 테이블 매핑용 (절대 create_all 하지 않음)
- QmsBase: 신규 qms_* 테이블용 (create_all 안전)
"""

from sqlalchemy.orm import declarative_base

# 기존 테이블 읽기 전용 매핑 (절대 create_all 금지)
ExistingBase = declarative_base()

# 신규 QMS 테이블용 베이스 (create_all 안전)
QmsBase = declarative_base()
