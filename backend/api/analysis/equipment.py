"""
설비별 분석 API 라우터
- 설비 가동능력 / ST 달성률 / 공정유형 점유율
"""

from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from services.analysis_service import (
    get_equipment_capacity,
    get_st_achievement,
    get_type_share,
)

router = APIRouter(prefix="/api/analysis/equipment", tags=["설비 분석"])


@router.get("/capacity")
def equipment_capacity(
    from_date: date = Query(..., alias="from", description="시작일"),
    to_date: date = Query(..., alias="to", description="종료일"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """설비 가동능력 분석"""
    items = get_equipment_capacity(db, from_date, to_date)
    return {"from_date": from_date, "to_date": to_date, "items": items}


@router.get("/standard-time-achievement")
def st_achievement(
    from_date: date = Query(..., alias="from", description="시작일"),
    to_date: date = Query(..., alias="to", description="종료일"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """표준시간(ST) 달성률 분석"""
    items = get_st_achievement(db, from_date, to_date)
    return {"from_date": from_date, "to_date": to_date, "items": items}


@router.get("/type-share")
def type_share(
    from_date: date = Query(..., alias="from", description="시작일"),
    to_date: date = Query(..., alias="to", description="종료일"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """공정유형 점유율 분석"""
    items = get_type_share(db, from_date, to_date)
    return {"from_date": from_date, "to_date": to_date, "items": items}
