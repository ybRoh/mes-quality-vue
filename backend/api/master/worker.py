"""
작업자 마스터 API 라우터 (읽기 전용)
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from api.quality.utils import escape_like
from config import settings
from models.existing import SysUser, Worker
from schemas.common import PagedResponse

router = APIRouter(prefix="/api/master/worker", tags=["작업자 마스터"])


@router.get("/")
def list_workers(
    page: int = Query(1, ge=1),
    size: int = Query(settings.MASTER_PAGE_SIZE, ge=1, le=settings.MASTER_MAX_PAGE_SIZE),
    department: Optional[str] = None,
    is_active: Optional[int] = 1,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """작업자 목록 조회"""
    query = db.query(Worker)
    if department:
        query = query.filter(Worker.department == department)
    if is_active is not None:
        query = query.filter(Worker.is_active == is_active)
    if search:
        query = query.filter(
            (Worker.worker_id.ilike(f"%{escape_like(search)}%")) |
            (Worker.worker_name.ilike(f"%{escape_like(search)}%"))
        )

    total = query.count()
    workers = query.order_by(Worker.worker_id).offset((page - 1) * size).limit(size).all()

    items = []
    for w in workers:
        items.append({
            "worker_id": w.worker_id,
            "worker_name": w.worker_name,
            "department": w.department,
            "shift": w.shift,
            "skill_level": w.skill_level,
            "phone": w.phone,
            "is_active": w.is_active,
        })

    pages = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/{worker_id}")
def get_worker(
    worker_id: str,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """작업자 상세 조회"""
    worker = db.query(Worker).filter(Worker.worker_id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="작업자를 찾을 수 없습니다")

    return {
        "worker_id": worker.worker_id,
        "worker_name": worker.worker_name,
        "department": worker.department,
        "shift": worker.shift,
        "skill_level": worker.skill_level,
        "phone": worker.phone,
        "is_active": worker.is_active,
    }
