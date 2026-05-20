"""
불량유형별 분석 API 라우터
- 유형별 점유율 (파레토), 제품별 불량, 월별 추이
"""

from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from services.analysis_service import (
    get_defect_by_type,
    get_defect_by_product,
    get_defect_trend,
)

router = APIRouter(prefix="/api/analysis/defect", tags=["불량유형별 분석"])


@router.get("/by-type")
def defect_by_type(
    from_date: date = Query(..., alias="from", description="시작일"),
    to_date: date = Query(..., alias="to", description="종료일"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """불량유형별 점유율 (파레토 분석)"""
    items = get_defect_by_type(db, from_date, to_date)
    return {"from_date": from_date, "to_date": to_date, "items": items}


@router.get("/by-product")
def defect_by_product(
    from_date: date = Query(..., alias="from", description="시작일"),
    to_date: date = Query(..., alias="to", description="종료일"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """제품별 불량 분석"""
    items = get_defect_by_product(db, from_date, to_date)
    return {"from_date": from_date, "to_date": to_date, "items": items}


@router.get("/trend")
def defect_trend(
    from_date: date = Query(..., alias="from", description="시작일"),
    to_date: date = Query(..., alias="to", description="종료일"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """불량유형별 월별 추이"""
    result = get_defect_trend(db, from_date, to_date)
    return {"from_date": from_date, "to_date": to_date, **result}
