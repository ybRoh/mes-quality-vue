"""
규격관리 API 라우터
- 규격 마스터, 도면 개정이력, SI FAQ, CSR CRUD
"""

import logging
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.deps import get_db, get_current_user, require_role
from core.audit import log_create, log_update, log_delete
from models.existing import SysUser
from models.iatf import (
    QmsSpecification, QmsDrawingRevision, QmsSiFaq, QmsCsr,
)
from schemas.specification import (
    SpecificationCreate, SpecificationUpdate, SpecificationResponse,
    DrawingRevisionCreate, DrawingRevisionResponse,
    SiFaqCreate, SiFaqUpdate, SiFaqResponse,
    CsrCreate, CsrUpdate, CsrResponse,
)
from schemas.common import PagedResponse
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/quality/specification", tags=["규격관리"])


# ============================================================
# SI FAQ (static paths must come before /{spec_id})
# ============================================================

@router.get("/si-faq", response_model=PagedResponse[SiFaqResponse])
def list_si_faq(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    customer_id: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    query = db.query(QmsSiFaq)
    if customer_id:
        query = query.filter(QmsSiFaq.customer_id == customer_id)
    if category:
        query = query.filter(QmsSiFaq.category == category)
    if is_active is not None:
        query = query.filter(QmsSiFaq.is_active == is_active)

    total = query.count()
    items = query.order_by(QmsSiFaq.created_at.desc()).offset((page - 1) * size).limit(size).all()
    pages = (total + size - 1) // size
    return PagedResponse(
        items=[SiFaqResponse.model_validate(f) for f in items],
        total=total, page=page, size=size, pages=pages,
    )


@router.post("/si-faq", response_model=SiFaqResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_si_faq(
    data: SiFaqCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    faq = QmsSiFaq(
        customer_id=data.customer_id, category=data.category,
        question=data.question, answer=data.answer,
        reference_spec_id=data.reference_spec_id, is_active=data.is_active,
    )
    db.add(faq)
    log_create(db, current_user.user_id, "qms_si_faq", str(faq.faq_id or "new"), "SI FAQ 생성")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(faq)
    return SiFaqResponse.model_validate(faq)


@router.put("/si-faq/{faq_id}", response_model=SiFaqResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def update_si_faq(
    faq_id: int, data: SiFaqUpdate,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    faq = db.query(QmsSiFaq).filter(QmsSiFaq.faq_id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ를 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(faq, key, None)
        setattr(faq, key, value)
        log_update(db, current_user.user_id, "qms_si_faq", str(faq.faq_id), key, old_value, value)

    faq.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(faq)
    return SiFaqResponse.model_validate(faq)


@router.delete("/si-faq/{faq_id}", dependencies=[Depends(require_role("ADMIN", "MANAGER"))])
def delete_si_faq(faq_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    faq = db.query(QmsSiFaq).filter(QmsSiFaq.faq_id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ를 찾을 수 없습니다")
    log_delete(db, current_user.user_id, "qms_si_faq", str(faq.faq_id), "SI FAQ 삭제")
    db.delete(faq)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "FAQ가 삭제되었습니다"}


# ============================================================
# CSR (static paths must come before /{spec_id})
# ============================================================

@router.get("/csr", response_model=PagedResponse[CsrResponse])
def list_csr(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    customer_id: Optional[str] = None,
    compliance_status: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    query = db.query(QmsCsr)
    if customer_id:
        query = query.filter(QmsCsr.customer_id == customer_id)
    if compliance_status:
        query = query.filter(QmsCsr.compliance_status == compliance_status)
    if category:
        query = query.filter(QmsCsr.category == category)

    total = query.count()
    items = query.order_by(QmsCsr.created_at.desc()).offset((page - 1) * size).limit(size).all()
    pages = (total + size - 1) // size
    return PagedResponse(
        items=[CsrResponse.model_validate(c) for c in items],
        total=total, page=page, size=size, pages=pages,
    )


@router.post("/csr", response_model=CsrResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_csr(
    data: CsrCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    existing = db.query(QmsCsr).filter(QmsCsr.csr_no == data.csr_no).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"CSR 번호 '{data.csr_no}'가 이미 존재합니다")

    csr = QmsCsr(
        csr_no=data.csr_no, customer_id=data.customer_id, requirement=data.requirement,
        category=data.category, iatf_clause=data.iatf_clause,
        compliance_status=data.compliance_status, responsible=data.responsible,
        target_date=data.target_date, evidence=data.evidence,
    )
    db.add(csr)
    log_create(db, current_user.user_id, "qms_csr", data.csr_no, "CSR 생성")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(csr)
    return CsrResponse.model_validate(csr)


@router.get("/csr/{csr_id}", response_model=CsrResponse)
def get_csr(csr_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    csr = db.query(QmsCsr).filter(QmsCsr.csr_id == csr_id).first()
    if not csr:
        raise HTTPException(status_code=404, detail="CSR을 찾을 수 없습니다")
    return CsrResponse.model_validate(csr)


@router.put("/csr/{csr_id}", response_model=CsrResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def update_csr(
    csr_id: int, data: CsrUpdate,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    csr = db.query(QmsCsr).filter(QmsCsr.csr_id == csr_id).first()
    if not csr:
        raise HTTPException(status_code=404, detail="CSR을 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(csr, key, None)
        setattr(csr, key, value)
        log_update(db, current_user.user_id, "qms_csr", csr.csr_no, key, old_value, value)

    csr.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(csr)
    return CsrResponse.model_validate(csr)


@router.delete("/csr/{csr_id}", dependencies=[Depends(require_role("ADMIN", "MANAGER"))])
def delete_csr(csr_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    csr = db.query(QmsCsr).filter(QmsCsr.csr_id == csr_id).first()
    if not csr:
        raise HTTPException(status_code=404, detail="CSR을 찾을 수 없습니다")
    log_delete(db, current_user.user_id, "qms_csr", csr.csr_no, "CSR 삭제")
    db.delete(csr)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "CSR이 삭제되었습니다"}


# ============================================================
# 규격 마스터
# ============================================================

@router.get("/", response_model=PagedResponse[SpecificationResponse])
def list_specifications(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    spec_type: Optional[str] = None,
    customer_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    query = db.query(QmsSpecification)
    if spec_type:
        query = query.filter(QmsSpecification.spec_type == spec_type)
    if customer_id:
        query = query.filter(QmsSpecification.customer_id == customer_id)
    if status:
        query = query.filter(QmsSpecification.status == status)

    total = query.count()
    specs = query.order_by(QmsSpecification.created_at.desc()).offset((page - 1) * size).limit(size).all()

    # batch load drawing counts
    spec_ids = [s.spec_mgmt_id for s in specs]
    drawing_counts = {}
    if spec_ids:
        dc = db.query(QmsDrawingRevision.spec_mgmt_id, func.count(QmsDrawingRevision.drawing_rev_id)).filter(
            QmsDrawingRevision.spec_mgmt_id.in_(spec_ids)
        ).group_by(QmsDrawingRevision.spec_mgmt_id).all()
        drawing_counts = {sid: cnt for sid, cnt in dc}

    items = []
    for s in specs:
        resp = SpecificationResponse.model_validate(s)
        resp.drawing_count = drawing_counts.get(s.spec_mgmt_id, 0)
        items.append(resp)

    pages = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.post("/", response_model=SpecificationResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_specification(
    data: SpecificationCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    existing = db.query(QmsSpecification).filter(QmsSpecification.spec_no == data.spec_no).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"규격 번호 '{data.spec_no}'가 이미 존재합니다")

    spec = QmsSpecification(
        spec_no=data.spec_no, spec_type=data.spec_type, customer_id=data.customer_id,
        product_id=data.product_id, title=data.title, revision=data.revision,
        status=data.status, effective_date=data.effective_date, expiry_date=data.expiry_date,
        source=data.source, remarks=data.remarks,
    )
    db.add(spec)
    log_create(db, current_user.user_id, "qms_specification", data.spec_no, "규격 생성")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(spec)
    resp = SpecificationResponse.model_validate(spec)
    resp.drawing_count = 0
    return resp


@router.get("/{spec_id}", response_model=SpecificationResponse)
def get_specification(spec_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    spec = db.query(QmsSpecification).filter(QmsSpecification.spec_mgmt_id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="규격을 찾을 수 없습니다")
    dc = db.query(func.count(QmsDrawingRevision.drawing_rev_id)).filter(
        QmsDrawingRevision.spec_mgmt_id == spec_id
    ).scalar()
    resp = SpecificationResponse.model_validate(spec)
    resp.drawing_count = dc
    return resp


@router.put("/{spec_id}", response_model=SpecificationResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def update_specification(
    spec_id: int, data: SpecificationUpdate,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    spec = db.query(QmsSpecification).filter(QmsSpecification.spec_mgmt_id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="규격을 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(spec, key, None)
        setattr(spec, key, value)
        log_update(db, current_user.user_id, "qms_specification", spec.spec_no, key, old_value, value)

    spec.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(spec)
    dc = db.query(func.count(QmsDrawingRevision.drawing_rev_id)).filter(
        QmsDrawingRevision.spec_mgmt_id == spec_id
    ).scalar()
    resp = SpecificationResponse.model_validate(spec)
    resp.drawing_count = dc
    return resp


@router.delete("/{spec_id}", dependencies=[Depends(require_role("ADMIN", "MANAGER"))])
def delete_specification(spec_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    spec = db.query(QmsSpecification).filter(QmsSpecification.spec_mgmt_id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="규격을 찾을 수 없습니다")

    # cascade delete drawings
    db.query(QmsDrawingRevision).filter(QmsDrawingRevision.spec_mgmt_id == spec_id).delete()

    log_delete(db, current_user.user_id, "qms_specification", spec.spec_no, "규격 삭제")
    db.delete(spec)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "규격이 삭제되었습니다"}


# ============================================================
# 도면 개정이력
# ============================================================

@router.get("/{spec_id}/drawings", response_model=List[DrawingRevisionResponse])
def list_drawings(
    spec_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    spec = db.query(QmsSpecification).filter(QmsSpecification.spec_mgmt_id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="규격을 찾을 수 없습니다")

    drawings = db.query(QmsDrawingRevision).filter(
        QmsDrawingRevision.spec_mgmt_id == spec_id
    ).order_by(QmsDrawingRevision.revision_no.desc()).all()

    return [DrawingRevisionResponse.model_validate(d) for d in drawings]


@router.post("/{spec_id}/drawings", response_model=DrawingRevisionResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_drawing(
    spec_id: int, data: DrawingRevisionCreate,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    spec = db.query(QmsSpecification).filter(QmsSpecification.spec_mgmt_id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="규격을 찾을 수 없습니다")

    drawing = QmsDrawingRevision(
        spec_mgmt_id=spec_id, drawing_no=data.drawing_no, revision_no=data.revision_no,
        change_summary=data.change_summary, changed_by=data.changed_by,
        change_date=data.change_date, file_path=data.file_path,
    )
    db.add(drawing)
    log_create(db, current_user.user_id, "qms_drawing_revision", data.drawing_no, "도면 개정이력 생성")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(drawing)
    return DrawingRevisionResponse.model_validate(drawing)
