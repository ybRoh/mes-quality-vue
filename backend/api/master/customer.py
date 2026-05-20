"""
거래선 마스터 API 라우터 (읽기 전용)
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from config import settings
from models.existing import SysUser, Customer
from schemas.common import PagedResponse

router = APIRouter(prefix="/api/master/customer", tags=["거래선 마스터"])


@router.get("/")
def list_customers(
    page: int = Query(1, ge=1),
    size: int = Query(settings.MASTER_PAGE_SIZE, ge=1, le=settings.MASTER_MAX_PAGE_SIZE),
    customer_type: Optional[str] = None,
    is_active: Optional[int] = 1,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """거래선 목록 조회"""
    query = db.query(Customer)
    if customer_type:
        query = query.filter(Customer.customer_type == customer_type)
    if is_active is not None:
        query = query.filter(Customer.is_active == is_active)
    if search:
        query = query.filter(
            (Customer.customer_id.contains(search)) |
            (Customer.customer_name.contains(search))
        )

    total = query.count()
    customers = query.order_by(Customer.customer_id).offset((page - 1) * size).limit(size).all()

    items = []
    for c in customers:
        items.append({
            "customer_id": c.customer_id,
            "customer_name": c.customer_name,
            "customer_type": c.customer_type,
            "contact_name": c.contact_name,
            "contact_phone": c.contact_phone,
            "is_active": c.is_active,
        })

    pages = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/{customer_id}")
def get_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """거래선 상세 조회"""
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="거래선을 찾을 수 없습니다")

    return {
        "customer_id": customer.customer_id,
        "customer_name": customer.customer_name,
        "customer_type": customer.customer_type,
        "contact_name": customer.contact_name,
        "contact_phone": customer.contact_phone,
        "is_active": customer.is_active,
    }
