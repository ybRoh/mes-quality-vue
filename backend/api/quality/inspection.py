"""
검사 관리 API 라우터 (읽기 전용)
- 검사 규격 조회
- 검사 실적 조회
- 검사 측정값 조회
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.deps import get_db, get_current_user
from api.quality.utils import escape_like
from models.existing import (
    SysUser, InspectionSpec, Inspection, InspectionValue,
    Product, Worker,
)

router = APIRouter(prefix="/api/quality/inspection", tags=["검사 관리"])


# ── 검사 규격 ──

@router.get("/specs")
def list_inspection_specs(
    product_id: Optional[str] = None,
    is_critical: Optional[int] = None,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """검사 규격 목록 조회"""
    query = db.query(InspectionSpec)
    if product_id:
        query = query.filter(InspectionSpec.product_id == product_id)
    if is_critical is not None:
        query = query.filter(InspectionSpec.is_critical == is_critical)

    total = query.count()
    specs = query.order_by(InspectionSpec.spec_id).offset((page - 1) * size).limit(size).all()

    # Batch load products
    spec_product_ids = list(set(s.product_id for s in specs if s.product_id))
    spec_products_map = {}
    if spec_product_ids:
        spec_products = db.query(Product).filter(Product.product_id.in_(spec_product_ids)).all()
        spec_products_map = {p.product_id: p for p in spec_products}

    items = []
    for s in specs:
        product = spec_products_map.get(s.product_id)
        items.append({
            "spec_id": s.spec_id,
            "product_id": s.product_id,
            "product_name": product.product_name if product else None,
            "insp_item": s.insp_item,
            "insp_type": s.insp_type,
            "spec_nominal": s.spec_nominal,
            "spec_usl": s.spec_usl,
            "spec_lsl": s.spec_lsl,
            "unit": s.unit,
            "method": s.method,
            "frequency": s.frequency,
            "is_critical": s.is_critical,
        })

    pages = (total + size - 1) // size
    return {"items": items, "total": total, "page": page, "size": size, "pages": pages}


@router.get("/specs/{spec_id}")
def get_inspection_spec(
    spec_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """검사 규격 상세 조회"""
    spec = db.query(InspectionSpec).filter(InspectionSpec.spec_id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="검사 규격을 찾을 수 없습니다")

    product = db.query(Product).filter(Product.product_id == spec.product_id).first() if spec.product_id else None
    return {
        "spec_id": spec.spec_id,
        "product_id": spec.product_id,
        "product_name": product.product_name if product else None,
        "insp_item": spec.insp_item,
        "insp_type": spec.insp_type,
        "spec_nominal": spec.spec_nominal,
        "spec_usl": spec.spec_usl,
        "spec_lsl": spec.spec_lsl,
        "unit": spec.unit,
        "method": spec.method,
        "frequency": spec.frequency,
        "is_critical": spec.is_critical,
    }


# ── 검사 실적 ──

@router.get("/records")
def list_inspections(
    product_id: Optional[str] = None,
    lot_no: Optional[str] = None,
    insp_stage: Optional[str] = None,
    result: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """검사 실적 목록 조회"""
    query = db.query(Inspection)
    if product_id:
        query = query.filter(Inspection.product_id == product_id)
    if lot_no:
        query = query.filter(Inspection.lot_no.ilike(f"%{escape_like(lot_no)}%"))
    if insp_stage:
        query = query.filter(Inspection.insp_stage == insp_stage)
    if result:
        query = query.filter(Inspection.result == result)

    total = query.count()
    inspections = query.order_by(Inspection.insp_date.desc()).offset((page - 1) * size).limit(size).all()

    # Batch load related entities to avoid N+1 queries
    product_ids = list(set(i.product_id for i in inspections if i.product_id))
    products_map = {}
    if product_ids:
        products = db.query(Product).filter(Product.product_id.in_(product_ids)).all()
        products_map = {p.product_id: p for p in products}

    inspector_ids = list(set(i.inspector_id for i in inspections if i.inspector_id))
    inspectors_map = {}
    if inspector_ids:
        inspectors = db.query(Worker).filter(Worker.worker_id.in_(inspector_ids)).all()
        inspectors_map = {w.worker_id: w for w in inspectors}

    items = []
    for insp in inspections:
        product = products_map.get(insp.product_id)
        inspector = inspectors_map.get(insp.inspector_id)
        items.append({
            "insp_id": insp.insp_id,
            "lot_no": insp.lot_no,
            "product_id": insp.product_id,
            "product_name": product.product_name if product else None,
            "insp_stage": insp.insp_stage,
            "inspector_id": insp.inspector_id,
            "inspector_name": inspector.worker_name if inspector else None,
            "insp_date": insp.insp_date,
            "insp_time": insp.insp_time,
            "result": insp.result,
            "remark": insp.remark,
        })

    pages = (total + size - 1) // size
    return {"items": items, "total": total, "page": page, "size": size, "pages": pages}


@router.get("/records/{insp_id}")
def get_inspection(
    insp_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """검사 실적 상세 (측정값 포함)"""
    insp = db.query(Inspection).filter(Inspection.insp_id == insp_id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="검사 실적을 찾을 수 없습니다")

    product = db.query(Product).filter(Product.product_id == insp.product_id).first() if insp.product_id else None

    # 측정값 조회 (batch load specs)
    values = db.query(InspectionValue).filter(InspectionValue.insp_id == insp_id).all()
    val_spec_ids = list(set(v.spec_id for v in values if v.spec_id))
    val_specs_map = {}
    if val_spec_ids:
        val_specs = db.query(InspectionSpec).filter(InspectionSpec.spec_id.in_(val_spec_ids)).all()
        val_specs_map = {s.spec_id: s for s in val_specs}

    value_list = []
    for v in values:
        spec = val_specs_map.get(v.spec_id)
        value_list.append({
            "value_id": v.value_id,
            "spec_id": v.spec_id,
            "insp_item": spec.insp_item if spec else None,
            "measured_value": v.measured_value,
            "judgment": v.judgment,
            "sample_no": v.sample_no,
            "spec_nominal": spec.spec_nominal if spec else None,
            "spec_usl": spec.spec_usl if spec else None,
            "spec_lsl": spec.spec_lsl if spec else None,
        })

    return {
        "insp_id": insp.insp_id,
        "lot_no": insp.lot_no,
        "product_id": insp.product_id,
        "product_name": product.product_name if product else None,
        "insp_stage": insp.insp_stage,
        "insp_date": insp.insp_date,
        "result": insp.result,
        "remark": insp.remark,
        "values": value_list,
    }
