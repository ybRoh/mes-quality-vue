"""
PPAP (생산부품승인절차) API 라우터
- PPAP 헤더 CRUD
- 18개 요소 체크리스트
- 완성도 계산
"""

import logging
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query

logger = logging.getLogger(__name__)
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.deps import get_db, get_current_user
from core.audit import log_create, log_update, log_delete
from models.existing import SysUser, Product, Customer
from models.iatf import QmsPpap, QmsPpapElement
from schemas.ppap import (
    PpapCreate, PpapUpdate, PpapResponse,
    PpapElementCreate, PpapElementUpdate, PpapElementResponse,
    PpapCompletenessResponse,
)
from schemas.common import PagedResponse
from config import settings

router = APIRouter(prefix="/api/quality/ppap", tags=["PPAP"])

# PPAP 18개 요소 정의
PPAP_18_ELEMENTS = [
    (1, "설계기록 (Design Records)"),
    (2, "설계변경문서 (Authorized Engineering Change Documents)"),
    (3, "고객 설계 승인 (Customer Engineering Approval)"),
    (4, "설계 FMEA (Design FMEA)"),
    (5, "공정흐름도 (Process Flow Diagram)"),
    (6, "공정 FMEA (Process FMEA)"),
    (7, "관리계획서 (Control Plan)"),
    (8, "측정시스템분석 (MSA Studies)"),
    (9, "치수결과 (Dimensional Results)"),
    (10, "재료시험결과 (Material/Performance Test Results)"),
    (11, "초기공정연구 (Initial Process Studies)"),
    (12, "자격인정 시험소 문서 (Qualified Laboratory Documentation)"),
    (13, "외관승인보고서 (Appearance Approval Report)"),
    (14, "양산시료 (Sample Production Parts)"),
    (15, "마스터시료 (Master Sample)"),
    (16, "검사구 (Checking Aids)"),
    (17, "고객 고유 요구사항 (Customer-Specific Requirements)"),
    (18, "부품제출보증서 (Part Submission Warrant - PSW)"),
]


# ── PPAP 헤더 ──

@router.get("/", response_model=PagedResponse[PpapResponse])
def list_ppaps(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    status: Optional[str] = None,
    product_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """PPAP 목록 조회"""
    query = db.query(QmsPpap)
    if status:
        query = query.filter(QmsPpap.status == status)
    if product_id:
        query = query.filter(QmsPpap.product_id == product_id)

    total = query.count()
    ppaps = query.order_by(QmsPpap.created_at.desc()).offset((page - 1) * size).limit(size).all()

    # Batch load related data
    product_ids = list(set(p.product_id for p in ppaps if p.product_id))
    products_map = {}
    if product_ids:
        products = db.query(Product).filter(Product.product_id.in_(product_ids)).all()
        products_map = {p.product_id: p for p in products}

    customer_ids = list(set(p.customer_id for p in ppaps if p.customer_id))
    customers_map = {}
    if customer_ids:
        custs = db.query(Customer).filter(Customer.customer_id.in_(customer_ids)).all()
        customers_map = {c.customer_id: c for c in custs}

    ppap_ids = [p.ppap_id for p in ppaps]
    elements_by_ppap = {}
    if ppap_ids:
        all_elements = db.query(QmsPpapElement).filter(QmsPpapElement.ppap_id.in_(ppap_ids)).all()
        for e in all_elements:
            elements_by_ppap.setdefault(e.ppap_id, []).append(e)

    items = []
    for p in ppaps:
        product = products_map.get(p.product_id)
        customer = customers_map.get(p.customer_id)

        # 완성도 계산
        elements = elements_by_ppap.get(p.ppap_id, [])
        required = [e for e in elements if e.is_required == 1]
        completed = [e for e in required if e.status == "COMPLETED"]
        completeness = round(len(completed) / len(required) * 100, 1) if required else 0.0

        items.append(PpapResponse(
            ppap_id=p.ppap_id,
            ppap_no=p.ppap_no,
            product_id=p.product_id,
            customer_id=p.customer_id,
            submission_level=p.submission_level,
            reason=p.reason,
            status=p.status,
            fmea_id=p.fmea_id,
            cp_id=p.cp_id,
            msa_id=p.msa_id,
            apqp_id=p.apqp_id,
            created_at=p.created_at,
            updated_at=p.updated_at,
            product_name=product.product_name if product else None,
            customer_name=customer.customer_name if customer else None,
            completeness_pct=completeness,
        ))

    pages = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.post("/", response_model=PpapResponse)
def create_ppap(
    data: PpapCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """PPAP 생성 (18개 요소 자동 초기화)"""
    existing = db.query(QmsPpap).filter(QmsPpap.ppap_no == data.ppap_no).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"PPAP 번호 '{data.ppap_no}'가 이미 존재합니다")

    ppap = QmsPpap(
        ppap_no=data.ppap_no,
        product_id=data.product_id,
        customer_id=data.customer_id,
        submission_level=data.submission_level,
        reason=data.reason,
        status=data.status,
        fmea_id=data.fmea_id,
        cp_id=data.cp_id,
        msa_id=data.msa_id,
        apqp_id=data.apqp_id,
    )
    db.add(ppap)
    db.flush()  # ppap_id 확보

    # 18개 요소 자동 생성
    for elem_no, elem_name in PPAP_18_ELEMENTS:
        element = QmsPpapElement(
            ppap_id=ppap.ppap_id,
            element_no=elem_no,
            element_name=elem_name,
            is_required=1,
            status="NOT_STARTED",
        )
        db.add(element)

    log_create(db, current_user.user_id, "qms_ppap", data.ppap_no, "PPAP 생성")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(ppap)

    product = db.query(Product).filter(Product.product_id == ppap.product_id).first()
    customer = db.query(Customer).filter(Customer.customer_id == ppap.customer_id).first() if ppap.customer_id else None

    return PpapResponse(
        ppap_id=ppap.ppap_id,
        ppap_no=ppap.ppap_no,
        product_id=ppap.product_id,
        customer_id=ppap.customer_id,
        submission_level=ppap.submission_level,
        reason=ppap.reason,
        status=ppap.status,
        fmea_id=ppap.fmea_id,
        cp_id=ppap.cp_id,
        msa_id=ppap.msa_id,
        apqp_id=ppap.apqp_id,
        created_at=ppap.created_at,
        updated_at=ppap.updated_at,
        product_name=product.product_name if product else None,
        customer_name=customer.customer_name if customer else None,
        completeness_pct=0.0,
    )


@router.get("/{ppap_id}", response_model=PpapResponse)
def get_ppap(
    ppap_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """PPAP 상세 조회"""
    ppap = db.query(QmsPpap).filter(QmsPpap.ppap_id == ppap_id).first()
    if not ppap:
        raise HTTPException(status_code=404, detail="PPAP를 찾을 수 없습니다")

    product = db.query(Product).filter(Product.product_id == ppap.product_id).first()
    customer = db.query(Customer).filter(Customer.customer_id == ppap.customer_id).first() if ppap.customer_id else None

    elements = db.query(QmsPpapElement).filter(QmsPpapElement.ppap_id == ppap_id).all()
    required = [e for e in elements if e.is_required == 1]
    completed = [e for e in required if e.status == "COMPLETED"]
    completeness = round(len(completed) / len(required) * 100, 1) if required else 0.0

    return PpapResponse(
        ppap_id=ppap.ppap_id,
        ppap_no=ppap.ppap_no,
        product_id=ppap.product_id,
        customer_id=ppap.customer_id,
        submission_level=ppap.submission_level,
        reason=ppap.reason,
        status=ppap.status,
        fmea_id=ppap.fmea_id,
        cp_id=ppap.cp_id,
        msa_id=ppap.msa_id,
        apqp_id=ppap.apqp_id,
        created_at=ppap.created_at,
        updated_at=ppap.updated_at,
        product_name=product.product_name if product else None,
        customer_name=customer.customer_name if customer else None,
        completeness_pct=completeness,
    )


@router.put("/{ppap_id}", response_model=PpapResponse)
def update_ppap(
    ppap_id: int,
    data: PpapUpdate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """PPAP 수정"""
    ppap = db.query(QmsPpap).filter(QmsPpap.ppap_id == ppap_id).first()
    if not ppap:
        raise HTTPException(status_code=404, detail="PPAP를 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(ppap, key)
        setattr(ppap, key, value)
        log_update(db, current_user.user_id, "qms_ppap", ppap.ppap_no, key, old_value, value)

    ppap.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(ppap)

    # 응답 구성 (간략화)
    return get_ppap(ppap_id, db, current_user)


@router.delete("/{ppap_id}")
def delete_ppap(
    ppap_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """PPAP 삭제"""
    ppap = db.query(QmsPpap).filter(QmsPpap.ppap_id == ppap_id).first()
    if not ppap:
        raise HTTPException(status_code=404, detail="PPAP를 찾을 수 없습니다")

    db.query(QmsPpapElement).filter(QmsPpapElement.ppap_id == ppap_id).delete()
    log_delete(db, current_user.user_id, "qms_ppap", ppap.ppap_no, "PPAP 삭제")
    db.delete(ppap)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "PPAP가 삭제되었습니다"}


# ── PPAP 요소 ──

@router.get("/{ppap_id}/elements", response_model=PpapCompletenessResponse)
def get_ppap_elements(
    ppap_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """PPAP 18개 요소 체크리스트 + 완성도"""
    ppap = db.query(QmsPpap).filter(QmsPpap.ppap_id == ppap_id).first()
    if not ppap:
        raise HTTPException(status_code=404, detail="PPAP를 찾을 수 없습니다")

    elements = db.query(QmsPpapElement).filter(
        QmsPpapElement.ppap_id == ppap_id
    ).order_by(QmsPpapElement.element_no).all()

    total_elements = len(elements)
    required = [e for e in elements if e.is_required == 1]
    completed = [e for e in required if e.status == "COMPLETED"]
    completeness = round(len(completed) / len(required) * 100, 1) if required else 0.0

    return PpapCompletenessResponse(
        ppap_id=ppap_id,
        total_elements=total_elements,
        required_elements=len(required),
        completed_elements=len(completed),
        completeness_pct=completeness,
        elements=[PpapElementResponse.model_validate(e) for e in elements],
    )


@router.put("/elements/{element_id}", response_model=PpapElementResponse)
def update_ppap_element(
    element_id: int,
    data: PpapElementUpdate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """PPAP 요소 상태 수정"""
    element = db.query(QmsPpapElement).filter(
        QmsPpapElement.element_id == element_id
    ).first()
    if not element:
        raise HTTPException(status_code=404, detail="PPAP 요소를 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(element, key, value)

    log_update(db, current_user.user_id, "qms_ppap_element", str(element_id),
               "status", None, data.status, "PPAP 요소 상태 변경")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(element)

    return PpapElementResponse.model_validate(element)
