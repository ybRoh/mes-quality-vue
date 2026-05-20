"""
클레임 (8D 프로세스) API 라우터
- 기존 claim 테이블 읽기/쓰기
- D1~D8 단계별 수정
"""

import logging
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query

logger = logging.getLogger(__name__)
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from core.audit import log_create, log_update
from models.existing import SysUser, Claim, Product, Customer
from schemas.claim import (
    ClaimCreate, ClaimResponse,
    ClaimD3Update, ClaimD4Update, ClaimD5Update,
    ClaimD6Update, ClaimD7Update, ClaimD8Update,
)
from schemas.common import PagedResponse
from config import settings

router = APIRouter(prefix="/api/quality/claim", tags=["클레임 8D"])


def _build_claim_response(claim: Claim, db: Session, products_map: dict = None, customers_map: dict = None) -> ClaimResponse:
    """Claim -> ClaimResponse 변환 헬퍼"""
    if products_map is not None:
        product = products_map.get(claim.product_id)
    else:
        product = db.query(Product).filter(Product.product_id == claim.product_id).first() if claim.product_id else None
    if customers_map is not None:
        customer = customers_map.get(claim.customer_id)
    else:
        customer = db.query(Customer).filter(Customer.customer_id == claim.customer_id).first() if claim.customer_id else None

    return ClaimResponse(
        claim_id=claim.claim_id,
        customer_id=claim.customer_id,
        product_id=claim.product_id,
        lot_no=claim.lot_no,
        claim_date=claim.claim_date,
        claim_qty=claim.claim_qty,
        defect_type=claim.defect_type,
        description=claim.description,
        cause=claim.cause,
        countermeasure=claim.countermeasure,
        status=claim.status,
        due_date=claim.due_date,
        created_at=claim.created_at,
        team_members=claim.team_members,
        defect_source=claim.defect_source,
        problem_definition=claim.problem_definition,
        immediate_action=claim.immediate_action,
        immediate_action_date=claim.immediate_action_date,
        cause_man=claim.cause_man,
        cause_machine=claim.cause_machine,
        cause_material=claim.cause_material,
        cause_method=claim.cause_method,
        why1=claim.why1,
        why2=claim.why2,
        why3=claim.why3,
        why4=claim.why4,
        why5=claim.why5,
        root_cause=claim.root_cause,
        corrective_action_date=claim.corrective_action_date,
        verification_result=claim.verification_result,
        verification_date=claim.verification_date,
        verification_by=claim.verification_by,
        deployment_targets=claim.deployment_targets,
        deployment_action=claim.deployment_action,
        deployment_date=claim.deployment_date,
        close_date=claim.close_date,
        close_approver=claim.close_approver,
        lessons_learned=claim.lessons_learned,
        customer_name=customer.customer_name if customer else None,
        product_name=product.product_name if product else None,
    )


@router.get("/", response_model=PagedResponse[ClaimResponse])
def list_claims(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    status: Optional[str] = None,
    customer_id: Optional[str] = None,
    product_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """클레임 목록 조회"""
    query = db.query(Claim)
    if status:
        query = query.filter(Claim.status == status)
    if customer_id:
        query = query.filter(Claim.customer_id == customer_id)
    if product_id:
        query = query.filter(Claim.product_id == product_id)

    total = query.count()
    claims = query.order_by(Claim.claim_date.desc()).offset((page - 1) * size).limit(size).all()

    # Batch load related data
    claim_product_ids = list(set(c.product_id for c in claims if c.product_id))
    claim_customer_ids = list(set(c.customer_id for c in claims if c.customer_id))
    products_map = {}
    customers_map = {}
    if claim_product_ids:
        prods = db.query(Product).filter(Product.product_id.in_(claim_product_ids)).all()
        products_map = {p.product_id: p for p in prods}
    if claim_customer_ids:
        custs = db.query(Customer).filter(Customer.customer_id.in_(claim_customer_ids)).all()
        customers_map = {c.customer_id: c for c in custs}

    items = [_build_claim_response(c, db, products_map, customers_map) for c in claims]

    pages = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/{claim_id}", response_model=ClaimResponse)
def get_claim(
    claim_id: str,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """클레임 상세 조회"""
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="클레임을 찾을 수 없습니다")
    return _build_claim_response(claim, db)


@router.post("/", response_model=ClaimResponse)
def create_claim(
    data: ClaimCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """클레임 등록 (D1/D2 단계)"""
    existing = db.query(Claim).filter(Claim.claim_id == data.claim_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"클레임 ID '{data.claim_id}'가 이미 존재합니다")

    claim = Claim(
        claim_id=data.claim_id,
        customer_id=data.customer_id,
        product_id=data.product_id,
        lot_no=data.lot_no,
        claim_date=data.claim_date,
        claim_qty=data.claim_qty,
        defect_type=data.defect_type,
        description=data.description,
        status=data.status,
        due_date=data.due_date,
        team_members=data.team_members,
        defect_source=data.defect_source,
        problem_definition=data.problem_definition,
    )
    db.add(claim)
    log_create(db, current_user.user_id, "claim", data.claim_id, "클레임 등록")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(claim)
    return _build_claim_response(claim, db)


@router.put("/{claim_id}/d3", response_model=ClaimResponse)
def update_claim_d3(
    claim_id: str,
    data: ClaimD3Update,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """D3: 즉각 조치 업데이트"""
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="클레임을 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(claim, key, value)

    if claim.status == "OPEN":
        claim.status = "IN_PROGRESS"

    log_update(db, current_user.user_id, "claim", claim_id, "d3", None, None, "D3 즉각조치 업데이트")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(claim)
    return _build_claim_response(claim, db)


@router.put("/{claim_id}/d4", response_model=ClaimResponse)
def update_claim_d4(
    claim_id: str,
    data: ClaimD4Update,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """D4: 원인 분석 업데이트"""
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="클레임을 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(claim, key, value)

    log_update(db, current_user.user_id, "claim", claim_id, "d4", None, None, "D4 원인분석 업데이트")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(claim)
    return _build_claim_response(claim, db)


@router.put("/{claim_id}/d5", response_model=ClaimResponse)
def update_claim_d5(
    claim_id: str,
    data: ClaimD5Update,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """D5: 시정 조치 업데이트"""
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="클레임을 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(claim, key, value)

    log_update(db, current_user.user_id, "claim", claim_id, "d5", None, None, "D5 시정조치 업데이트")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(claim)
    return _build_claim_response(claim, db)


@router.put("/{claim_id}/d6", response_model=ClaimResponse)
def update_claim_d6(
    claim_id: str,
    data: ClaimD6Update,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """D6: 유효성 검증 업데이트"""
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="클레임을 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(claim, key, value)

    log_update(db, current_user.user_id, "claim", claim_id, "d6", None, None, "D6 유효성검증 업데이트")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(claim)
    return _build_claim_response(claim, db)


@router.put("/{claim_id}/d7", response_model=ClaimResponse)
def update_claim_d7(
    claim_id: str,
    data: ClaimD7Update,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """D7: 수평 전개 업데이트"""
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="클레임을 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(claim, key, value)

    log_update(db, current_user.user_id, "claim", claim_id, "d7", None, None, "D7 수평전개 업데이트")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(claim)
    return _build_claim_response(claim, db)


@router.put("/{claim_id}/d8", response_model=ClaimResponse)
def update_claim_d8(
    claim_id: str,
    data: ClaimD8Update,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """D8: 완료 업데이트"""
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="클레임을 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(claim, key, value)

    log_update(db, current_user.user_id, "claim", claim_id, "d8", None, None, "D8 완료 업데이트")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(claim)
    return _build_claim_response(claim, db)
