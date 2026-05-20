"""
품번별 분석 API 라우터
- 생산시간 / ST 달성률 / 상세 실적
"""

from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from services.analysis_service import (
    get_spec_production_time,
    get_spec_st_achievement,
    get_spec_detail,
)

router = APIRouter(prefix="/api/analysis/specification", tags=["품번 분석"])


@router.get("/production-time")
def spec_production_time(
    from_date: date = Query(..., alias="from", description="시작일"),
    to_date: date = Query(..., alias="to", description="종료일"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """품번별 생산시간 분석"""
    items = get_spec_production_time(db, from_date, to_date)
    return {"from_date": from_date, "to_date": to_date, "items": items}


@router.get("/st-achievement")
def spec_st_achievement(
    from_date: date = Query(..., alias="from", description="시작일"),
    to_date: date = Query(..., alias="to", description="종료일"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """품번별 ST 달성률 분석"""
    items = get_spec_st_achievement(db, from_date, to_date)
    return {"from_date": from_date, "to_date": to_date, "items": items}


@router.get("/detail")
def spec_detail(
    from_date: date = Query(..., alias="from", description="시작일"),
    to_date: date = Query(..., alias="to", description="종료일"),
    product_id: str = Query(..., description="품번"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """품번 상세 생산실적"""
    items = get_spec_detail(db, from_date, to_date, product_id)
    return {
        "from_date": from_date,
        "to_date": to_date,
        "product_id": product_id,
        "items": items,
    }
