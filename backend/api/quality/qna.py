"""
Q&A 질문/답변 API 라우터
- 목록/상세/질문등록: 로그인 없이 이용 가능 (비로그인 시 이메일 필수)
- 답변/수정/삭제/마감: 로그인 필요
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from api.deps import get_db, get_current_user, get_optional_user, require_role
from api.quality.utils import escape_like, validate_qna_content
from core.audit import log_create, log_update, log_delete
from models.existing import SysUser
from models.iatf import QmsQna
from schemas.qna import QnaCreate, QnaUpdate, QnaAnswer, QnaResponse
from schemas.common import PagedResponse
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/quality/qna", tags=["Q&A"])


# ============================================================
# Q&A 목록 조회 (공개)
# ============================================================

@router.get("/", response_model=PagedResponse[QnaResponse])
def list_qna(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    category: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[SysUser] = Depends(get_optional_user),
):
    query = db.query(QmsQna)
    if category:
        query = query.filter(QmsQna.category == category)
    if status:
        query = query.filter(QmsQna.status == status)
    if search:
        like_pattern = f"%{escape_like(search)}%"
        query = query.filter(
            or_(
                QmsQna.title.ilike(like_pattern),
                QmsQna.question.ilike(like_pattern),
            )
        )

    total = query.count()
    items = query.order_by(QmsQna.created_at.desc()).offset((page - 1) * size).limit(size).all()
    pages = (total + size - 1) // size
    return PagedResponse(
        items=[QnaResponse.model_validate(q) for q in items],
        total=total, page=page, size=size, pages=pages,
    )


# ============================================================
# Q&A 등록 (공개 - 비로그인 시 이메일 필수)
# ============================================================

@router.post("/", response_model=QnaResponse)
def create_qna(
    data: QnaCreate,
    db: Session = Depends(get_db),
    current_user: Optional[SysUser] = Depends(get_optional_user),
):
    # 비로그인 사용자는 이메일 필수
    if not current_user and not data.author_email:
        raise HTTPException(status_code=400, detail="로그인하지 않은 경우 이메일 주소가 필요합니다")

    # 콘텐츠 필터링
    for field_name, field_value in [("제목", data.title), ("질문", data.question)]:
        violation = validate_qna_content(field_value)
        if violation:
            raise HTTPException(status_code=400, detail=f"{field_name}: {violation}")

    qna = QmsQna(
        title=data.title,
        question=data.question,
        category=data.category,
        is_public=data.is_public,
        author_id=current_user.user_id if current_user else None,
        author_name=data.author_name or (current_user.user_name if current_user else None),
        author_email=data.author_email,
    )
    db.add(qna)

    user_id = current_user.user_id if current_user else (data.author_email or "anonymous")
    log_create(db, user_id, "qms_qna", str(qna.qna_id or "new"), "Q&A 질문 등록")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(qna)
    return QnaResponse.model_validate(qna)


# ============================================================
# Q&A 상세 조회 (공개)
# ============================================================

@router.get("/{qna_id}", response_model=QnaResponse)
def get_qna(
    qna_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[SysUser] = Depends(get_optional_user),
):
    qna = db.query(QmsQna).filter(QmsQna.qna_id == qna_id).first()
    if not qna:
        raise HTTPException(status_code=404, detail="Q&A를 찾을 수 없습니다")

    # 조회수 증가
    qna.view_count = (qna.view_count or 0) + 1
    try:
        db.commit()
    except Exception:
        db.rollback()
    db.refresh(qna)
    return QnaResponse.model_validate(qna)


# ============================================================
# Q&A 수정 (작성자 또는 ADMIN만 - 로그인 필요)
# ============================================================

@router.put("/{qna_id}", response_model=QnaResponse)
def update_qna(
    qna_id: int,
    data: QnaUpdate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    qna = db.query(QmsQna).filter(QmsQna.qna_id == qna_id).first()
    if not qna:
        raise HTTPException(status_code=404, detail="Q&A를 찾을 수 없습니다")

    # 작성자 또는 ADMIN만 수정 가능
    if qna.author_id != current_user.user_id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="수정 권한이 없습니다")

    update_data = data.model_dump(exclude_unset=True)

    # 콘텐츠 필터링 (title, question 변경 시)
    filter_fields = {"title": "제목", "question": "질문"}
    for key, value in update_data.items():
        if key in filter_fields and isinstance(value, str):
            violation = validate_qna_content(value)
            if violation:
                raise HTTPException(status_code=400, detail=f"{filter_fields[key]}: {violation}")

    for key, value in update_data.items():
        old_value = getattr(qna, key, None)
        setattr(qna, key, value)
        log_update(db, current_user.user_id, "qms_qna", str(qna.qna_id), key, old_value, value)

    qna.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(qna)
    return QnaResponse.model_validate(qna)


# ============================================================
# Q&A 삭제 (ADMIN, MANAGER만 - 로그인 필요)
# ============================================================

@router.delete("/{qna_id}", dependencies=[Depends(require_role("ADMIN", "MANAGER"))])
def delete_qna(
    qna_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    qna = db.query(QmsQna).filter(QmsQna.qna_id == qna_id).first()
    if not qna:
        raise HTTPException(status_code=404, detail="Q&A를 찾을 수 없습니다")

    log_delete(db, current_user.user_id, "qms_qna", str(qna.qna_id), "Q&A 삭제")
    db.delete(qna)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "Q&A가 삭제되었습니다"}


# ============================================================
# Q&A 답변 등록 (ADMIN, MANAGER, QA_ENGINEER만 - 로그인 필요)
# ============================================================

@router.post("/{qna_id}/answer", response_model=QnaResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def answer_qna(
    qna_id: int,
    data: QnaAnswer,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    qna = db.query(QmsQna).filter(QmsQna.qna_id == qna_id).first()
    if not qna:
        raise HTTPException(status_code=404, detail="Q&A를 찾을 수 없습니다")

    # 답변 콘텐츠 필터링
    violation = validate_qna_content(data.answer)
    if violation:
        raise HTTPException(status_code=400, detail=f"답변: {violation}")

    old_answer = getattr(qna, "answer", None)
    qna.answer = data.answer
    qna.answered_by = current_user.user_id
    qna.answered_at = datetime.now(timezone.utc)
    qna.status = "ANSWERED"
    qna.updated_at = datetime.now(timezone.utc)

    log_update(db, current_user.user_id, "qms_qna", str(qna.qna_id), "answer", old_answer, data.answer)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(qna)
    return QnaResponse.model_validate(qna)


# ============================================================
# Q&A 마감 (작성자 또는 ADMIN만 - 로그인 필요)
# ============================================================

@router.put("/{qna_id}/close", response_model=QnaResponse)
def close_qna(
    qna_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    qna = db.query(QmsQna).filter(QmsQna.qna_id == qna_id).first()
    if not qna:
        raise HTTPException(status_code=404, detail="Q&A를 찾을 수 없습니다")

    # 작성자 또는 ADMIN만 마감 가능
    if qna.author_id != current_user.user_id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="마감 권한이 없습니다")

    old_status = qna.status
    qna.status = "CLOSED"
    qna.updated_at = datetime.now(timezone.utc)

    log_update(db, current_user.user_id, "qms_qna", str(qna.qna_id), "status", old_status, "CLOSED")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(qna)
    return QnaResponse.model_validate(qna)
