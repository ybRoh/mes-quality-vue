"""
품번 마스터 API 라우터 (읽기 전용)
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from api.quality.utils import escape_like
from config import settings
from models.existing import SysUser, Product, Customer
from schemas.common import PagedResponse

router = APIRouter(prefix="/api/master/product", tags=["품번 마스터"])


@router.get("/")
def list_products(
    page: int = Query(1, ge=1),
    size: int = Query(settings.MASTER_PAGE_SIZE, ge=1, le=settings.MASTER_MAX_PAGE_SIZE),
    process_type: Optional[str] = None,
    customer_id: Optional[str] = None,
    is_active: Optional[int] = 1,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """품번 목록 조회"""
    query = db.query(Product)
    if process_type:
        query = query.filter(Product.process_type == process_type)
    if customer_id:
        query = query.filter(Product.customer_id == customer_id)
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    if search:
        query = query.filter(
            (Product.product_id.ilike(f"%{escape_like(search)}%")) |
            (Product.product_name.ilike(f"%{escape_like(search)}%"))
        )

    total = query.count()
    products = query.order_by(Product.product_id).offset((page - 1) * size).limit(size).all()

    # Batch load customers to avoid N+1
    customer_ids = list(set(p.customer_id for p in products if p.customer_id))
    customers_map = {}
    if customer_ids:
        custs = db.query(Customer).filter(Customer.customer_id.in_(customer_ids)).all()
        customers_map = {c.customer_id: c for c in custs}

    items = []
    for p in products:
        customer = customers_map.get(p.customer_id)
        items.append({
            "product_id": p.product_id,
            "product_name": p.product_name,
            "customer_id": p.customer_id,
            "customer_name": customer.customer_name if customer else None,
            "customer_part_no": p.customer_part_no,
            "process_type": p.process_type,
            "material_type": p.material_type,
            "cavity": p.cavity,
            "cycle_time": p.cycle_time,
            "unit_weight": p.unit_weight,
            "drawing_no": p.drawing_no,
            "is_active": p.is_active,
        })

    pages = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/{product_id}")
def get_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """품번 상세 조회"""
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="품번을 찾을 수 없습니다")

    customer = db.query(Customer).filter(Customer.customer_id == product.customer_id).first() if product.customer_id else None
    return {
        "product_id": product.product_id,
        "product_name": product.product_name,
        "customer_id": product.customer_id,
        "customer_name": customer.customer_name if customer else None,
        "customer_part_no": product.customer_part_no,
        "process_type": product.process_type,
        "material_type": product.material_type,
        "cavity": product.cavity,
        "cycle_time": product.cycle_time,
        "unit_weight": product.unit_weight,
        "drawing_no": product.drawing_no,
        "is_active": product.is_active,
    }
