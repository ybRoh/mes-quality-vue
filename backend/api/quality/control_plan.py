"""
Control Plan (관리계획서) API 라우터
- Control Plan 헤더 CRUD
- Control Plan 항목 CRUD
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
from models.iatf import QmsControlPlan, QmsControlPlanItem
from schemas.control_plan import (
    ControlPlanCreate, ControlPlanUpdate, ControlPlanResponse,
    ControlPlanItemCreate, ControlPlanItemUpdate, ControlPlanItemResponse,
)
from schemas.common import PagedResponse
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/quality/control-plan", tags=["Control Plan"])


def _build_cp_response(cp: QmsControlPlan, db: Session, products_map: dict = None) -> ControlPlanResponse:
    """ControlPlan → ControlPlanResponse 변환 헬퍼"""
    if products_map is not None:
        product = products_map.get(cp.product_id)
    else:
        product = db.query(Product).filter(Product.product_id == cp.product_id).first()

    item_count = db.query(func.count(QmsControlPlanItem.cp_item_id)).filter(
        QmsControlPlanItem.cp_id == cp.cp_id
    ).scalar()

    return ControlPlanResponse(
        cp_id=cp.cp_id,
        cp_no=cp.cp_no,
        product_id=cp.product_id,
        fmea_id=cp.fmea_id,
        cp_type=cp.cp_type,
        revision=cp.revision,
        status=cp.status,
        prepared_by=cp.prepared_by,
        approved_by=cp.approved_by,
        created_at=cp.created_at,
        updated_at=cp.updated_at,
        product_name=product.product_name if product else None,
        item_count=item_count,
    )


# ── Control Plan 헤더 ──

@router.get("/", response_model=PagedResponse[ControlPlanResponse])
def list_control_plans(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    status: Optional[str] = None,
    product_id: Optional[str] = None,
    cp_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """Control Plan 목록 조회"""
    query = db.query(QmsControlPlan)
    if status:
        query = query.filter(QmsControlPlan.status == status)
    if product_id:
        query = query.filter(QmsControlPlan.product_id == product_id)
    if cp_type:
        query = query.filter(QmsControlPlan.cp_type == cp_type)

    total = query.count()
    cps = query.order_by(QmsControlPlan.created_at.desc()).offset((page - 1) * size).limit(size).all()

    # Batch load related data
    product_ids = list(set(cp.product_id for cp in cps if cp.product_id))
    products_map = {}
    if product_ids:
        products = db.query(Product).filter(Product.product_id.in_(product_ids)).all()
        products_map = {p.product_id: p for p in products}

    cp_ids = [cp.cp_id for cp in cps]
    item_counts = {}
    if cp_ids:
        counts = db.query(QmsControlPlanItem.cp_id, func.count(QmsControlPlanItem.cp_item_id)).filter(
            QmsControlPlanItem.cp_id.in_(cp_ids)
        ).group_by(QmsControlPlanItem.cp_id).all()
        item_counts = {cp_id: cnt for cp_id, cnt in counts}

    items = []
    for cp in cps:
        product = products_map.get(cp.product_id)
        items.append(ControlPlanResponse(
            cp_id=cp.cp_id,
            cp_no=cp.cp_no,
            product_id=cp.product_id,
            fmea_id=cp.fmea_id,
            cp_type=cp.cp_type,
            revision=cp.revision,
            status=cp.status,
            prepared_by=cp.prepared_by,
            approved_by=cp.approved_by,
            created_at=cp.created_at,
            updated_at=cp.updated_at,
            product_name=product.product_name if product else None,
            item_count=item_counts.get(cp.cp_id, 0),
        ))

    pages = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.post("/", response_model=ControlPlanResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_control_plan(
    data: ControlPlanCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """Control Plan 생성"""
    existing = db.query(QmsControlPlan).filter(QmsControlPlan.cp_no == data.cp_no).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"CP 번호 '{data.cp_no}'가 이미 존재합니다")

    cp = QmsControlPlan(
        cp_no=data.cp_no,
        product_id=data.product_id,
        fmea_id=data.fmea_id,
        cp_type=data.cp_type,
        revision=data.revision,
        status=data.status,
        prepared_by=data.prepared_by or current_user.user_id,
        approved_by=data.approved_by,
    )
    db.add(cp)
    log_create(db, current_user.user_id, "qms_control_plan", data.cp_no, "Control Plan 생성")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(cp)

    return _build_cp_response(cp, db)


# ── Control Plan 항목 (static-prefix routes before parameterized /{cp_id}) ──

@router.put("/items/{cp_item_id}", response_model=ControlPlanItemResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def update_cp_item(
    cp_item_id: int,
    data: ControlPlanItemUpdate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """Control Plan 항목 수정"""
    item = db.query(QmsControlPlanItem).filter(
        QmsControlPlanItem.cp_item_id == cp_item_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="CP 항목을 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    log_update(db, current_user.user_id, "qms_control_plan_item", str(cp_item_id), "update", None, None, "CP 항목 수정")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(item)

    return ControlPlanItemResponse.model_validate(item)


@router.delete("/items/{cp_item_id}", dependencies=[Depends(require_role("ADMIN", "MANAGER"))])
def delete_cp_item(
    cp_item_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """Control Plan 항목 삭제"""
    item = db.query(QmsControlPlanItem).filter(
        QmsControlPlanItem.cp_item_id == cp_item_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="CP 항목을 찾을 수 없습니다")

    log_delete(db, current_user.user_id, "qms_control_plan_item", str(cp_item_id), "CP 항목 삭제")
    db.delete(item)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "CP 항목이 삭제되었습니다"}


# ── Control Plan 헤더 (parameterized /{cp_id} routes) ──

@router.get("/{cp_id}", response_model=ControlPlanResponse)
def get_control_plan(
    cp_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """Control Plan 상세 조회"""
    cp = db.query(QmsControlPlan).filter(QmsControlPlan.cp_id == cp_id).first()
    if not cp:
        raise HTTPException(status_code=404, detail="Control Plan을 찾을 수 없습니다")

    return _build_cp_response(cp, db)


@router.put("/{cp_id}", response_model=ControlPlanResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def update_control_plan(
    cp_id: int,
    data: ControlPlanUpdate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """Control Plan 수정"""
    cp = db.query(QmsControlPlan).filter(QmsControlPlan.cp_id == cp_id).first()
    if not cp:
        raise HTTPException(status_code=404, detail="Control Plan을 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(cp, key, None)
        setattr(cp, key, value)
        log_update(db, current_user.user_id, "qms_control_plan", cp.cp_no, key, old_value, value)

    cp.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(cp)

    return _build_cp_response(cp, db)


@router.delete("/{cp_id}", dependencies=[Depends(require_role("ADMIN", "MANAGER"))])
def delete_control_plan(
    cp_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """Control Plan 삭제"""
    cp = db.query(QmsControlPlan).filter(QmsControlPlan.cp_id == cp_id).first()
    if not cp:
        raise HTTPException(status_code=404, detail="Control Plan을 찾을 수 없습니다")

    db.query(QmsControlPlanItem).filter(QmsControlPlanItem.cp_id == cp_id).delete(synchronize_session=False)
    log_delete(db, current_user.user_id, "qms_control_plan", cp.cp_no, "Control Plan 삭제")
    db.delete(cp)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "Control Plan이 삭제되었습니다"}


@router.get("/{cp_id}/items", response_model=List[ControlPlanItemResponse])
def list_cp_items(
    cp_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """Control Plan 항목 목록 조회"""
    cp = db.query(QmsControlPlan).filter(QmsControlPlan.cp_id == cp_id).first()
    if not cp:
        raise HTTPException(status_code=404, detail="Control Plan을 찾을 수 없습니다")

    items = db.query(QmsControlPlanItem).filter(
        QmsControlPlanItem.cp_id == cp_id
    ).order_by(QmsControlPlanItem.process_no).all()

    return [ControlPlanItemResponse.model_validate(item) for item in items]


@router.post("/{cp_id}/items", response_model=ControlPlanItemResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_cp_item(
    cp_id: int,
    data: ControlPlanItemCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """Control Plan 항목 추가"""
    cp = db.query(QmsControlPlan).filter(QmsControlPlan.cp_id == cp_id).first()
    if not cp:
        raise HTTPException(status_code=404, detail="Control Plan을 찾을 수 없습니다")

    item = QmsControlPlanItem(
        cp_id=cp_id,
        process_no=data.process_no,
        process_name=data.process_name,
        machine_id=data.machine_id,
        characteristic_name=data.characteristic_name,
        characteristic_class=data.characteristic_class,
        spec_id=data.spec_id,
        evaluation_method=data.evaluation_method,
        sample_size=data.sample_size,
        sample_frequency=data.sample_frequency,
        control_method=data.control_method,
        reaction_plan=data.reaction_plan,
    )
    db.add(item)
    log_create(db, current_user.user_id, "qms_control_plan_item", str(cp_id), "CP 항목 추가")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(item)

    return ControlPlanItemResponse.model_validate(item)
