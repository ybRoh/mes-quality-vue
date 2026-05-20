"""
생산분석 Pydantic 스키마
- 기간별, 유형별, 설비별, 품번별 분석 응답 모델
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import date


# ============================================================
# 기간별 분석 (Period)
# ============================================================

class DailyProductionItem(BaseModel):
    """일별 생산 항목"""
    product_id: str
    product_name: Optional[str] = None
    machine_id: Optional[str] = None
    machine_name: Optional[str] = None
    plan_qty: int = 0
    good_qty: int = 0
    ng_qty: int = 0
    total_qty: int = 0
    ng_rate: float = 0.0
    achievement_rate: float = 0.0


class DailyProductionResponse(BaseModel):
    """일별 생산 응답"""
    date: date
    items: List[DailyProductionItem]
    total_plan: int = 0
    total_good: int = 0
    total_ng: int = 0


class MonthlyProductionItem(BaseModel):
    """월별 생산 항목"""
    work_date: date
    plan_qty: int = 0
    good_qty: int = 0
    ng_qty: int = 0
    total_qty: int = 0
    ng_rate: float = 0.0
    achievement_rate: float = 0.0
    production_count: int = 0


class MonthlyProductionResponse(BaseModel):
    """월별 생산 응답"""
    year: int
    month: int
    items: List[MonthlyProductionItem]
    total_plan: int = 0
    total_good: int = 0
    total_ng: int = 0


class YearlyProductionItem(BaseModel):
    """연별 생산 항목"""
    month: int
    plan_qty: int = 0
    good_qty: int = 0
    ng_qty: int = 0
    total_qty: int = 0
    ng_rate: float = 0.0
    production_count: int = 0


# ============================================================
# 설비별 분석 (Equipment)
# ============================================================

class EquipmentAnalysisItem(BaseModel):
    """설비별 분석 항목"""
    machine_id: str
    machine_name: Optional[str] = None
    process_type: Optional[str] = None
    plan_qty: int = 0
    good_qty: int = 0
    ng_qty: int = 0
    total_qty: int = 0
    ng_rate: float = 0.0
    achievement_rate: float = 0.0
    operating_hours: float = 0.0


class EquipmentCapacityItem(BaseModel):
    """설비 가동능력 항목"""
    machine_id: str
    machine_name: Optional[str] = None
    process_type: Optional[str] = None
    total_qty: int = 0
    operating_hours: float = 0.0
    capacity_rate: float = 0.0
    avg_cycle_time: Optional[float] = None


class StAchievementItem(BaseModel):
    """ST(표준시간) 달성률 항목"""
    machine_id: str
    machine_name: Optional[str] = None
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    std_cycle_time: Optional[float] = None
    avg_cycle_time: Optional[float] = None
    st_achievement: float = 0.0
    production_count: int = 0


class TypeShareItem(BaseModel):
    """공정유형 점유율 항목"""
    process_type: str
    process_name: Optional[str] = None
    total_qty: int = 0
    share_pct: float = 0.0
    machine_count: int = 0


# ============================================================
# 품번별 분석 (Specification)
# ============================================================

class SpecAnalysisItem(BaseModel):
    """품번별 분석 항목"""
    product_id: str
    product_name: Optional[str] = None
    process_type: Optional[str] = None
    plan_qty: int = 0
    good_qty: int = 0
    ng_qty: int = 0
    total_qty: int = 0
    ng_rate: float = 0.0
    achievement_rate: float = 0.0


class SpecProductionTimeItem(BaseModel):
    """품번별 생산시간 분석 항목"""
    product_id: str
    product_name: Optional[str] = None
    total_qty: int = 0
    operating_hours: float = 0.0
    avg_cycle_time: Optional[float] = None
    std_cycle_time: Optional[float] = None


class SpecStAchievementItem(BaseModel):
    """품번별 ST 달성률 항목"""
    product_id: str
    product_name: Optional[str] = None
    std_cycle_time: Optional[float] = None
    avg_cycle_time: Optional[float] = None
    st_achievement: float = 0.0
    total_qty: int = 0


class SpecDetailItem(BaseModel):
    """품번 상세 분석 항목"""
    work_date: date
    machine_id: Optional[str] = None
    machine_name: Optional[str] = None
    lot_no: Optional[str] = None
    plan_qty: int = 0
    good_qty: int = 0
    ng_qty: int = 0
    cycle_time_avg: Optional[float] = None
    worker_id: Optional[str] = None


# ============================================================
# 유형별 분석 (Type)
# ============================================================

class MonthlyTrendItem(BaseModel):
    """월별 추이 항목"""
    year_month: str
    plan_qty: int = 0
    good_qty: int = 0
    ng_qty: int = 0
    ng_rate: float = 0.0
    production_count: int = 0


class ProductionShareItem(BaseModel):
    """생산 점유율 항목"""
    product_id: str
    product_name: Optional[str] = None
    total_qty: int = 0
    share_pct: float = 0.0


class PartsCompositionItem(BaseModel):
    """부품 구성비 항목"""
    product_id: str
    product_name: Optional[str] = None
    process_type: Optional[str] = None
    good_qty: int = 0
    ng_qty: int = 0
    total_qty: int = 0
    composition_pct: float = 0.0


class CustomerTypeItem(BaseModel):
    """고객유형별 분석 항목"""
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_type: Optional[str] = None
    total_qty: int = 0
    good_qty: int = 0
    ng_qty: int = 0
    share_pct: float = 0.0
