"""
유형별 분석 API 라우터
- 생산 점유율 / 부품 구성비 / 고객유형별 분석
"""

from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from services.analysis_service import (
    get_production_share,
    get_parts_composition,
    get_by_customer,
)

router = APIRouter(prefix="/api/analysis/type", tags=["유형별 분석"])


@router.get("/production-share")
def production_share(
    from_date: date = Query(..., alias="from", description="시작일"),
    to_date: date = Query(..., alias="to", description="종료일"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """생산 점유율 분석"""
    items = get_production_share(db, from_date, to_date)
    return {"from_date": from_date, "to_date": to_date, "items": items}


@router.get("/parts-composition")
def parts_composition(
    from_date: date = Query(..., alias="from", description="시작일"),
    to_date: date = Query(..., alias="to", description="종료일"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """부품 구성비 분석"""
    items = get_parts_composition(db, from_date, to_date)
    return {"from_date": from_date, "to_date": to_date, "items": items}


@router.get("/by-customer")
def by_customer(
    from_date: date = Query(..., alias="from", description="시작일"),
    to_date: date = Query(..., alias="to", description="종료일"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """고객유형별 생산 분석"""
    items = get_by_customer(db, from_date, to_date)
    return {"from_date": from_date, "to_date": to_date, "items": items}
