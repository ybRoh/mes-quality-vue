"""
FMEA (고장모드 영향분석) API 라우터
- FMEA 헤더 CRUD
- FMEA 항목 CRUD
- RPN 분석
"""

import logging
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.deps import get_db, get_current_user, require_role
from core.audit import log_create, log_update, log_delete
from models.existing import SysUser, Product
from models.iatf import QmsFmea, QmsFmeaItem
from schemas.fmea import (
    FmeaCreate, FmeaUpdate, FmeaResponse,
    FmeaItemCreate, FmeaItemUpdate, FmeaItemResponse,
    RpnAnalysisResponse,
)
from schemas.common import PagedResponse
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/quality/fmea", tags=["FMEA"])


def _build_fmea_response(fmea: QmsFmea, db: Session, products_map: dict = None) -> FmeaResponse:
    """FMEA → FmeaResponse 변환 헬퍼"""
    if products_map is not None:
        product = products_map.get(fmea.product_id)
    else:
        product = db.query(Product).filter(Product.product_id == fmea.product_id).first()

    item_count = db.query(func.count(QmsFmeaItem.item_id)).filter(
        QmsFmeaItem.fmea_id == fmea.fmea_id
    ).scalar()

    return FmeaResponse(
        fmea_id=fmea.fmea_id,
        fmea_no=fmea.fmea_no,
        product_id=fmea.product_id,
        fmea_type=fmea.fmea_type,
        revision=fmea.revision,
        status=fmea.status,
        prepared_by=fmea.prepared_by,
        approved_by=fmea.approved_by,
        created_at=fmea.created_at,
        updated_at=fmea.updated_at,
        product_name=product.product_name if product else None,
        item_count=item_count,
    )


# ── FMEA 헤더 ──

@router.get("/", response_model=PagedResponse[FmeaResponse])
def list_fmeas(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    status: Optional[str] = None,
    product_id: Optional[str] = None,
    fmea_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """FMEA 목록 조회"""
    query = db.query(QmsFmea)
    if status:
        query = query.filter(QmsFmea.status == status)
    if product_id:
        query = query.filter(QmsFmea.product_id == product_id)
    if fmea_type:
        query = query.filter(QmsFmea.fmea_type == fmea_type)

    total = query.count()
    fmeas = query.order_by(QmsFmea.created_at.desc()).offset((page - 1) * size).limit(size).all()

    # Batch load related data
    product_ids = list(set(f.product_id for f in fmeas if f.product_id))
    products_map = {}
    if product_ids:
        products = db.query(Product).filter(Product.product_id.in_(product_ids)).all()
        products_map = {p.product_id: p for p in products}

    fmea_ids = [f.fmea_id for f in fmeas]
    item_counts = {}
    if fmea_ids:
        counts = db.query(QmsFmeaItem.fmea_id, func.count(QmsFmeaItem.item_id)).filter(
            QmsFmeaItem.fmea_id.in_(fmea_ids)
        ).group_by(QmsFmeaItem.fmea_id).all()
        item_counts = {fmea_id: cnt for fmea_id, cnt in counts}

    items = []
    for f in fmeas:
        product = products_map.get(f.product_id)
        items.append(FmeaResponse(
            fmea_id=f.fmea_id,
            fmea_no=f.fmea_no,
            product_id=f.product_id,
            fmea_type=f.fmea_type,
            revision=f.revision,
            status=f.status,
            prepared_by=f.prepared_by,
            approved_by=f.approved_by,
            created_at=f.created_at,
            updated_at=f.updated_at,
            product_name=product.product_name if product else None,
            item_count=item_counts.get(f.fmea_id, 0),
        ))

    pages = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.post("/", response_model=FmeaResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_fmea(
    data: FmeaCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """FMEA 생성"""
    # 중복 확인
    existing = db.query(QmsFmea).filter(QmsFmea.fmea_no == data.fmea_no).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"FMEA 번호 '{data.fmea_no}'가 이미 존재합니다")

    fmea = QmsFmea(
        fmea_no=data.fmea_no,
        product_id=data.product_id,
        fmea_type=data.fmea_type,
        revision=data.revision,
        status=data.status,
        prepared_by=data.prepared_by or current_user.user_id,
        approved_by=data.approved_by,
    )
    db.add(fmea)
    log_create(db, current_user.user_id, "qms_fmea", data.fmea_no, "FMEA 생성")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(fmea)

    return _build_fmea_response(fmea, db)


@router.get("/{fmea_id}", response_model=FmeaResponse)
def get_fmea(
    fmea_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """FMEA 상세 조회"""
    fmea = db.query(QmsFmea).filter(QmsFmea.fmea_id == fmea_id).first()
    if not fmea:
        raise HTTPException(status_code=404, detail="FMEA를 찾을 수 없습니다")

    return _build_fmea_response(fmea, db)


@router.put("/{fmea_id}", response_model=FmeaResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def update_fmea(
    fmea_id: int,
    data: FmeaUpdate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """FMEA 수정"""
    fmea = db.query(QmsFmea).filter(QmsFmea.fmea_id == fmea_id).first()
    if not fmea:
        raise HTTPException(status_code=404, detail="FMEA를 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(fmea, key, None)
        setattr(fmea, key, value)
        log_update(db, current_user.user_id, "qms_fmea", fmea.fmea_no, key, old_value, value)

    fmea.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(fmea)

    return _build_fmea_response(fmea, db)


@router.delete("/{fmea_id}", dependencies=[Depends(require_role("ADMIN", "MANAGER"))])
def delete_fmea(
    fmea_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """FMEA 삭제"""
    fmea = db.query(QmsFmea).filter(QmsFmea.fmea_id == fmea_id).first()
    if not fmea:
        raise HTTPException(status_code=404, detail="FMEA를 찾을 수 없습니다")

    # 하위 항목 먼저 삭제
    db.query(QmsFmeaItem).filter(QmsFmeaItem.fmea_id == fmea_id).delete()
    log_delete(db, current_user.user_id, "qms_fmea", fmea.fmea_no, "FMEA 삭제")
    db.delete(fmea)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "FMEA가 삭제되었습니다"}


# ── FMEA 항목 ──

@router.get("/{fmea_id}/items", response_model=PagedResponse[FmeaItemResponse])
def list_fmea_items(
    fmea_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """FMEA 항목 목록 조회"""
    fmea = db.query(QmsFmea).filter(QmsFmea.fmea_id == fmea_id).first()
    if not fmea:
        raise HTTPException(status_code=404, detail="FMEA를 찾을 수 없습니다")

    query = db.query(QmsFmeaItem).filter(
        QmsFmeaItem.fmea_id == fmea_id
    ).order_by(QmsFmeaItem.item_id)

    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()

    pages = (total + size - 1) // size
    return PagedResponse(
        items=[FmeaItemResponse.model_validate(item) for item in items],
        total=total, page=page, size=size, pages=pages,
    )


@router.post("/{fmea_id}/items", response_model=FmeaItemResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_fmea_item(
    fmea_id: int,
    data: FmeaItemCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """FMEA 항목 추가"""
    fmea = db.query(QmsFmea).filter(QmsFmea.fmea_id == fmea_id).first()
    if not fmea:
        raise HTTPException(status_code=404, detail="FMEA를 찾을 수 없습니다")

    # RPN 자동 계산
    rpn = data.severity * data.occurrence * data.detection
    # AP (조치우선순위) 결정
    if rpn >= 100:
        ap = "H"
    elif rpn >= 50:
        ap = "M"
    else:
        ap = "L"

    # 개선 후 RPN
    new_rpn = None
    if data.new_severity and data.new_occurrence and data.new_detection:
        new_rpn = data.new_severity * data.new_occurrence * data.new_detection

    item = QmsFmeaItem(
        fmea_id=fmea_id,
        process_step=data.process_step,
        function_requirement=data.function_requirement,
        failure_mode=data.failure_mode,
        failure_effect=data.failure_effect,
        severity=data.severity,
        failure_cause=data.failure_cause,
        occurrence=data.occurrence,
        current_control_prevent=data.current_control_prevent,
        current_control_detect=data.current_control_detect,
        detection=data.detection,
        rpn=rpn,
        ap=ap,
        recommended_action=data.recommended_action,
        responsible=data.responsible,
        target_date=data.target_date,
        action_taken=data.action_taken,
        new_severity=data.new_severity,
        new_occurrence=data.new_occurrence,
        new_detection=data.new_detection,
        new_rpn=new_rpn,
    )
    db.add(item)
    log_create(db, current_user.user_id, "qms_fmea_item", str(fmea_id), f"FMEA 항목 추가: {data.failure_mode}")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(item)

    return FmeaItemResponse.model_validate(item)


@router.put("/items/{item_id}", response_model=FmeaItemResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def update_fmea_item(
    item_id: int,
    data: FmeaItemUpdate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """FMEA 항목 수정"""
    item = db.query(QmsFmeaItem).filter(QmsFmeaItem.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="FMEA 항목을 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    # RPN 재계산
    item.rpn = item.severity * item.occurrence * item.detection
    if item.rpn >= 100:
        item.ap = "H"
    elif item.rpn >= 50:
        item.ap = "M"
    else:
        item.ap = "L"

    # 개선 후 RPN 재계산
    if item.new_severity and item.new_occurrence and item.new_detection:
        item.new_rpn = item.new_severity * item.new_occurrence * item.new_detection

    log_update(db, current_user.user_id, "qms_fmea_item", str(item_id), "update", None, None, "FMEA 항목 수정")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(item)

    return FmeaItemResponse.model_validate(item)


# ── RPN 분석 ──

@router.get("/{fmea_id}/rpn-analysis", response_model=RpnAnalysisResponse)
def rpn_analysis(
    fmea_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """RPN 분석"""
    fmea = db.query(QmsFmea).filter(QmsFmea.fmea_id == fmea_id).first()
    if not fmea:
        raise HTTPException(status_code=404, detail="FMEA를 찾을 수 없습니다")

    items = db.query(QmsFmeaItem).filter(
        QmsFmeaItem.fmea_id == fmea_id
    ).order_by(QmsFmeaItem.rpn.desc()).all()

    total_items = len(items)
    high_count = sum(1 for i in items if (i.rpn or 0) >= 100)
    medium_count = sum(1 for i in items if 50 <= (i.rpn or 0) < 100)
    low_count = sum(1 for i in items if (i.rpn or 0) < 50)
    avg_rpn = sum(i.rpn or 0 for i in items) / total_items if total_items > 0 else 0
    max_rpn = max((i.rpn or 0) for i in items) if items else 0

    # 상위 5개 RPN 항목
    top_items = [FmeaItemResponse.model_validate(i) for i in items[:5]]

    return RpnAnalysisResponse(
        fmea_id=fmea_id,
        total_items=total_items,
        high_rpn_count=high_count,
        medium_rpn_count=medium_count,
        low_rpn_count=low_count,
        avg_rpn=round(avg_rpn, 1),
        max_rpn=max_rpn,
        top_rpn_items=top_items,
    )
