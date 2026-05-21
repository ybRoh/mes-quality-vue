"""
표준문서관리 API 라우터
- 문서 CRUD + 워크플로우(승인/폐기) + 개정이력 + 첨부파일
"""

import logging
import os
import uuid
from datetime import datetime, timezone, date
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.deps import get_db, get_current_user, require_role
from core.audit import log_create, log_update, log_delete
from models.existing import SysUser
from models.iatf import QmsDocument, QmsDocumentRevision, QmsDocumentAttachment
from schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentResponse,
    DocumentRevisionCreate, DocumentRevisionResponse,
    DocumentAttachmentResponse,
)
from schemas.common import PagedResponse
from config import settings
from api.quality.utils import escape_like

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/quality/document", tags=["표준문서관리"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _build_doc_response(doc: QmsDocument, db: Session) -> DocumentResponse:
    rev_count = db.query(func.count(QmsDocumentRevision.revision_id)).filter(
        QmsDocumentRevision.doc_id == doc.doc_id
    ).scalar()
    att_count = db.query(func.count(QmsDocumentAttachment.attachment_id)).filter(
        QmsDocumentAttachment.doc_id == doc.doc_id
    ).scalar()
    return DocumentResponse(
        doc_id=doc.doc_id,
        doc_no=doc.doc_no,
        doc_type=doc.doc_type,
        title=doc.title,
        department=doc.department,
        revision=doc.revision,
        status=doc.status,
        prepared_by=doc.prepared_by,
        reviewed_by=doc.reviewed_by,
        approved_by=doc.approved_by,
        effective_date=doc.effective_date,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        revision_count=rev_count,
        attachment_count=att_count,
    )


# ── 문서 CRUD ──

@router.get("/", response_model=PagedResponse[DocumentResponse])
def list_documents(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    doc_type: Optional[str] = None,
    status: Optional[str] = None,
    department: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """문서 목록 조회"""
    query = db.query(QmsDocument)
    if doc_type:
        query = query.filter(QmsDocument.doc_type == doc_type)
    if status:
        query = query.filter(QmsDocument.status == status)
    if department:
        query = query.filter(QmsDocument.department == department)
    if keyword:
        query = query.filter(QmsDocument.title.ilike(f"%{escape_like(keyword)}%"))

    total = query.count()
    docs = query.order_by(QmsDocument.updated_at.desc()).offset((page - 1) * size).limit(size).all()

    doc_ids = [d.doc_id for d in docs]
    rev_counts = {}
    att_counts = {}
    if doc_ids:
        rc = db.query(QmsDocumentRevision.doc_id, func.count(QmsDocumentRevision.revision_id)).filter(
            QmsDocumentRevision.doc_id.in_(doc_ids)
        ).group_by(QmsDocumentRevision.doc_id).all()
        rev_counts = {did: cnt for did, cnt in rc}
        ac = db.query(QmsDocumentAttachment.doc_id, func.count(QmsDocumentAttachment.attachment_id)).filter(
            QmsDocumentAttachment.doc_id.in_(doc_ids)
        ).group_by(QmsDocumentAttachment.doc_id).all()
        att_counts = {did: cnt for did, cnt in ac}

    items = []
    for d in docs:
        items.append(DocumentResponse(
            doc_id=d.doc_id, doc_no=d.doc_no, doc_type=d.doc_type, title=d.title,
            department=d.department, revision=d.revision, status=d.status,
            prepared_by=d.prepared_by, reviewed_by=d.reviewed_by, approved_by=d.approved_by,
            effective_date=d.effective_date, created_at=d.created_at, updated_at=d.updated_at,
            revision_count=rev_counts.get(d.doc_id, 0),
            attachment_count=att_counts.get(d.doc_id, 0),
        ))

    pages = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.post("/", response_model=DocumentResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_document(
    data: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """문서 생성"""
    existing = db.query(QmsDocument).filter(QmsDocument.doc_no == data.doc_no).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"문서번호 '{data.doc_no}'가 이미 존재합니다")

    doc = QmsDocument(
        doc_no=data.doc_no,
        doc_type=data.doc_type,
        title=data.title,
        department=data.department,
        revision=data.revision,
        status=data.status,
        prepared_by=data.prepared_by or current_user.user_id,
        reviewed_by=data.reviewed_by,
        approved_by=data.approved_by,
        effective_date=data.effective_date,
    )
    db.add(doc)
    log_create(db, current_user.user_id, "qms_document", data.doc_no, "문서 생성")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(doc)
    return _build_doc_response(doc, db)


# ── 첨부파일 (static-prefix routes before parameterized /{doc_id}) ──

@router.delete("/attachments/{attachment_id}", dependencies=[Depends(require_role("ADMIN", "MANAGER"))])
def delete_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """첨부파일 삭제"""
    att = db.query(QmsDocumentAttachment).filter(
        QmsDocumentAttachment.attachment_id == attachment_id
    ).first()
    if not att:
        raise HTTPException(status_code=404, detail="첨부파일을 찾을 수 없습니다")

    if os.path.exists(att.file_path):
        os.remove(att.file_path)

    log_delete(db, current_user.user_id, "qms_document_attachment", str(attachment_id), f"첨부파일 삭제: {att.file_name}")
    db.delete(att)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "첨부파일이 삭제되었습니다"}


@router.get("/attachments/{attachment_id}/download")
def download_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """첨부파일 다운로드"""
    att = db.query(QmsDocumentAttachment).filter(
        QmsDocumentAttachment.attachment_id == attachment_id
    ).first()
    if not att:
        raise HTTPException(status_code=404, detail="첨부파일을 찾을 수 없습니다")

    if not os.path.exists(att.file_path):
        raise HTTPException(status_code=404, detail="파일이 서버에 존재하지 않습니다")

    # 경로 탐색 공격 방지
    resolved = os.path.realpath(att.file_path)
    if not resolved.startswith(os.path.realpath(UPLOAD_DIR)):
        raise HTTPException(status_code=400, detail="잘못된 파일 경로")

    return FileResponse(
        path=att.file_path,
        filename=att.file_name,
        media_type=att.mime_type or "application/octet-stream",
    )


# ── 문서 상세/수정/삭제 (parameterized /{doc_id} routes) ──

@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """문서 상세 조회"""
    doc = db.query(QmsDocument).filter(QmsDocument.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")
    return _build_doc_response(doc, db)


@router.put("/{doc_id}", response_model=DocumentResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def update_document(
    doc_id: int,
    data: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """문서 수정"""
    doc = db.query(QmsDocument).filter(QmsDocument.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(doc, key)
        setattr(doc, key, value)
        log_update(db, current_user.user_id, "qms_document", doc.doc_no, key, old_value, value)

    doc.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(doc)
    return _build_doc_response(doc, db)


@router.delete("/{doc_id}", dependencies=[Depends(require_role("ADMIN", "MANAGER"))])
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """문서 삭제"""
    doc = db.query(QmsDocument).filter(QmsDocument.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")

    # 첨부파일 물리 삭제
    attachments = db.query(QmsDocumentAttachment).filter(QmsDocumentAttachment.doc_id == doc_id).all()
    for att in attachments:
        if os.path.exists(att.file_path):
            os.remove(att.file_path)

    db.query(QmsDocumentAttachment).filter(QmsDocumentAttachment.doc_id == doc_id).delete()
    db.query(QmsDocumentRevision).filter(QmsDocumentRevision.doc_id == doc_id).delete()
    log_delete(db, current_user.user_id, "qms_document", doc.doc_no, "문서 삭제")
    db.delete(doc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "문서가 삭제되었습니다"}


# ── 워크플로우 ──

@router.put("/{doc_id}/approve", response_model=DocumentResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def approve_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """문서 승인 (DRAFT→REVIEW→APPROVED)"""
    doc = db.query(QmsDocument).filter(QmsDocument.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")

    old_status = doc.status
    if doc.status == "DRAFT":
        doc.status = "REVIEW"
        doc.reviewed_by = current_user.user_id
    elif doc.status == "REVIEW":
        doc.status = "APPROVED"
        doc.approved_by = current_user.user_id
        doc.effective_date = date.today()
    else:
        raise HTTPException(status_code=400, detail=f"현재 상태({doc.status})에서는 승인할 수 없습니다")

    # 개정이력 자동 생성
    rev = QmsDocumentRevision(
        doc_id=doc_id,
        revision_no=doc.revision,
        change_summary=f"상태 변경: {old_status} → {doc.status}",
        changed_by=current_user.user_id,
        previous_status=old_status,
        new_status=doc.status,
    )
    db.add(rev)

    doc.updated_at = datetime.now(timezone.utc)
    log_update(db, current_user.user_id, "qms_document", doc.doc_no, "status", old_status, doc.status)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(doc)
    return _build_doc_response(doc, db)


@router.put("/{doc_id}/obsolete", response_model=DocumentResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def obsolete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """문서 폐기"""
    doc = db.query(QmsDocument).filter(QmsDocument.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")

    old_status = doc.status
    doc.status = "OBSOLETE"

    rev = QmsDocumentRevision(
        doc_id=doc_id,
        revision_no=doc.revision,
        change_summary=f"문서 폐기: {old_status} → OBSOLETE",
        changed_by=current_user.user_id,
        previous_status=old_status,
        new_status="OBSOLETE",
    )
    db.add(rev)

    doc.updated_at = datetime.now(timezone.utc)
    log_update(db, current_user.user_id, "qms_document", doc.doc_no, "status", old_status, "OBSOLETE")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(doc)
    return _build_doc_response(doc, db)


# ── 개정이력 ──

@router.get("/{doc_id}/revisions", response_model=List[DocumentRevisionResponse])
def list_revisions(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """문서 개정이력 목록"""
    doc = db.query(QmsDocument).filter(QmsDocument.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")

    revs = db.query(QmsDocumentRevision).filter(
        QmsDocumentRevision.doc_id == doc_id
    ).order_by(QmsDocumentRevision.created_at.desc()).all()
    return [DocumentRevisionResponse.model_validate(r) for r in revs]


@router.post("/{doc_id}/revisions", response_model=DocumentRevisionResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_revision(
    doc_id: int,
    data: DocumentRevisionCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """문서 개정이력 추가"""
    doc = db.query(QmsDocument).filter(QmsDocument.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")

    rev = QmsDocumentRevision(
        doc_id=doc_id,
        revision_no=data.revision_no,
        change_summary=data.change_summary,
        changed_by=data.changed_by or current_user.user_id,
        previous_status=data.previous_status,
        new_status=data.new_status,
    )
    db.add(rev)

    # 문서 revision 번호 갱신
    doc.revision = data.revision_no
    doc.updated_at = datetime.now(timezone.utc)

    log_create(db, current_user.user_id, "qms_document_revision", str(doc_id), f"개정이력 추가: Rev.{data.revision_no}")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(rev)
    return DocumentRevisionResponse.model_validate(rev)


# ── 첨부파일 (parameterized /{doc_id}/attachments routes) ──

@router.get("/{doc_id}/attachments", response_model=List[DocumentAttachmentResponse])
def list_attachments(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """문서 첨부파일 목록"""
    doc = db.query(QmsDocument).filter(QmsDocument.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")

    atts = db.query(QmsDocumentAttachment).filter(
        QmsDocumentAttachment.doc_id == doc_id
    ).order_by(QmsDocumentAttachment.created_at.desc()).all()
    return [DocumentAttachmentResponse.model_validate(a) for a in atts]


@router.post("/{doc_id}/attachments", response_model=DocumentAttachmentResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
async def upload_attachment(
    doc_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """문서 첨부파일 업로드"""
    doc = db.query(QmsDocument).filter(QmsDocument.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")

    # 파일 확장자 검증
    ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.csv', '.txt'}
    ext = os.path.splitext(file.filename or '')[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"허용되지 않는 파일 형식입니다: {ext}")

    # 파일 크기 제한 (50MB)
    MAX_FILE_SIZE = 50 * 1024 * 1024
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="파일 크기가 50MB를 초과합니다")

    # 고유 파일명 생성
    stored_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, stored_name)

    # 경로 탐색 공격 방지
    resolved = os.path.realpath(file_path)
    if not resolved.startswith(os.path.realpath(UPLOAD_DIR)):
        raise HTTPException(status_code=400, detail="잘못된 파일 경로")

    with open(file_path, "wb") as f:
        f.write(content)

    att = QmsDocumentAttachment(
        doc_id=doc_id,
        file_name=file.filename or stored_name,
        file_path=file_path,
        file_size=len(content),
        mime_type=file.content_type,
        uploaded_by=current_user.user_id,
    )
    db.add(att)
    log_create(db, current_user.user_id, "qms_document_attachment", str(doc_id), f"첨부파일 업로드: {file.filename}")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(att)
    return DocumentAttachmentResponse.model_validate(att)
