"""
감사 로깅 유틸리티
- 기존 audit_log 테이블에 변경 이력 기록
- CREATE / UPDATE / DELETE 액션 추적
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models.existing import AuditLog


def log_audit(
    db: Session,
    user_id: str,
    action: str,
    table_name: str,
    record_id: str,
    field_name: str = None,
    old_value: str = None,
    new_value: str = None,
    description: str = None,
):
    """감사 로그 기록"""
    log = AuditLog(
        timestamp=datetime.now(timezone.utc),
        user_id=user_id,
        action=action,
        table_name=table_name,
        record_id=str(record_id),
        field_name=field_name,
        old_value=str(old_value) if old_value is not None else None,
        new_value=str(new_value) if new_value is not None else None,
        description=description,
    )
    db.add(log)
    # 감사 로그는 별도 커밋하지 않음 (호출자의 트랜잭션에 포함)


def log_create(db: Session, user_id: str, table_name: str, record_id: str, description: str = None):
    """생성 감사 로그"""
    log_audit(db, user_id, "CREATE", table_name, record_id, description=description)


def log_update(
    db: Session,
    user_id: str,
    table_name: str,
    record_id: str,
    field_name: str,
    old_value=None,
    new_value=None,
    description: str = None,
):
    """수정 감사 로그"""
    log_audit(db, user_id, "UPDATE", table_name, record_id,
              field_name=field_name, old_value=old_value, new_value=new_value,
              description=description)


def log_delete(db: Session, user_id: str, table_name: str, record_id: str, description: str = None):
    """삭제 감사 로그"""
    log_audit(db, user_id, "DELETE", table_name, record_id, description=description)
