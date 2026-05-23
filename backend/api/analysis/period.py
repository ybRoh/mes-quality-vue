"""
기간별 분석 API 라우터
- 일별 / 월별 / 연별 / 설비별 / 품번별 / 월추이 생산실적 분석
"""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from services.analysis_service import (
    get_daily_production,
    get_monthly_production,
    get_yearly_production,
    get_by_equipment,
    get_by_spec,
    get_monthly_trend,
)

router = APIRouter(prefix="/api/analysis/period", tags=["기간별 분석"])


@router.get("/daily")
def daily_production(
    query_date: date = Query(..., alias="date", description="조회 날짜"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """일별 생산실적 조회"""
    items = get_daily_production(db, query_date)
    total_plan = sum(i["plan_qty"] for i in items)
    total_good = sum(i["good_qty"] for i in items)
    total_ng = sum(i["ng_qty"] for i in items)
    return {
        "date": query_date,
        "items": items,
        "total_plan": total_plan,
        "total_good": total_good,
        "total_ng": total_ng,
    }


@router.get("/monthly")
def monthly_production(
    year: int = Query(..., description="연도"),
    month: int = Query(..., description="월"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """월별 생산실적 (일자별 집계)"""
    items = get_monthly_production(db, year, month)
    total_plan = sum(i["plan_qty"] for i in items)
    total_good = sum(i["good_qty"] for i in items)
    total_ng = sum(i["ng_qty"] for i in items)
    return {
        "year": year,
        "month": month,
        "items": items,
        "total_plan": total_plan,
        "total_good": total_good,
        "total_ng": total_ng,
    }


@router.get("/yearly")
def yearly_production(
    year: int = Query(..., description="연도"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """연별 생산실적 (월별 집계)"""
    items = get_yearly_production(db, year)
    return {"year": year, "items": items}


@router.get("/by-equipment")
def by_equipment(
    from_date: date = Query(..., alias="from", description="시작일"),
    to_date: date = Query(..., alias="to", description="종료일"),
    machine_id: Optional[str] = Query(None, description="설비 ID (선택)"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """설비별 생산실적 분석"""
    items = get_by_equipment(db, from_date, to_date, machine_id)
    return {"from_date": from_date, "to_date": to_date, "items": items}


@router.get("/by-spec")
def by_spec(
    from_date: date = Query(..., alias="from", description="시작일"),
    to_date: date = Query(..., alias="to", description="종료일"),
    product_id: Optional[str] = Query(None, description="품번 (선택)"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """품번별 생산실적 분석"""
    items = get_by_spec(db, from_date, to_date, product_id)
    return {"from_date": from_date, "to_date": to_date, "items": items}


@router.get("/monthly-trend")
def monthly_trend(
    from_date: date = Query(..., alias="from", description="시작일"),
    to_date: date = Query(..., alias="to", description="종료일"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """월별 추이 분석"""
    items = get_monthly_trend(db, from_date, to_date)
    return {"from_date": from_date, "to_date": to_date, "items": items}
