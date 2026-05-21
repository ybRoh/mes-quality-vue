"""
설비 마스터 API 라우터 (읽기 전용)
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from api.quality.utils import escape_like
from config import settings
from models.existing import SysUser, Machine, Line, Factory
from schemas.common import PagedResponse

router = APIRouter(prefix="/api/master/machine", tags=["설비 마스터"])


@router.get("/")
def list_machines(
    page: int = Query(1, ge=1),
    size: int = Query(settings.MASTER_PAGE_SIZE, ge=1, le=settings.MASTER_MAX_PAGE_SIZE),
    process_type: Optional[str] = None,
    line_id: Optional[str] = None,
    is_active: Optional[int] = 1,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """설비 목록 조회"""
    query = db.query(Machine)
    if process_type:
        query = query.filter(Machine.process_type == process_type)
    if line_id:
        query = query.filter(Machine.line_id == line_id)
    if is_active is not None:
        query = query.filter(Machine.is_active == is_active)
    if search:
        query = query.filter(
            (Machine.machine_id.ilike(f"%{escape_like(search)}%")) |
            (Machine.machine_name.ilike(f"%{escape_like(search)}%"))
        )

    total = query.count()
    machines = query.order_by(Machine.machine_id).offset((page - 1) * size).limit(size).all()

    items = []
    for m in machines:
        line = db.query(Line).filter(Line.line_id == m.line_id).first() if m.line_id else None
        items.append({
            "machine_id": m.machine_id,
            "machine_name": m.machine_name,
            "line_id": m.line_id,
            "line_name": line.line_name if line else None,
            "process_type": m.process_type,
            "maker": m.maker,
            "model": m.model,
            "serial_no": m.serial_no,
            "install_date": m.install_date,
            "is_active": m.is_active,
        })

    pages = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/{machine_id}")
def get_machine(
    machine_id: str,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """설비 상세 조회"""
    machine = db.query(Machine).filter(Machine.machine_id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="설비를 찾을 수 없습니다")

    line = db.query(Line).filter(Line.line_id == machine.line_id).first() if machine.line_id else None
    return {
        "machine_id": machine.machine_id,
        "machine_name": machine.machine_name,
        "line_id": machine.line_id,
        "line_name": line.line_name if line else None,
        "process_type": machine.process_type,
        "maker": machine.maker,
        "model": machine.model,
        "serial_no": machine.serial_no,
        "install_date": machine.install_date,
        "is_active": machine.is_active,
    }
