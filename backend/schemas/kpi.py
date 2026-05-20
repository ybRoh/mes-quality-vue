"""
성과지표관리 Pydantic 스키마
- KPI 정의, KPI 데이터, 대시보드, 공정모니터링, 리스크/이슈
"""

from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import Literal, Optional, List


# ============================================================
# KPI 정의 (Definition)
# ============================================================

class KpiDefinitionCreate(BaseModel):
    kpi_no: str
    kpi_name: str
    process_name: Optional[str] = None
    category: Optional[str] = None          # 품질/납기/원가/안전
    unit: Optional[str] = None              # %, ppm, 건
    target_value: Optional[float] = None
    target_direction: Literal["HIGHER", "LOWER"] = "HIGHER"
    threshold_yellow: Optional[float] = None
    threshold_red: Optional[float] = None
    measurement_frequency: Literal["DAILY", "WEEKLY", "MONTHLY", "QUARTERLY", "YEARLY"] = "MONTHLY"
    responsible: Optional[str] = None
    formula: Optional[str] = None
    is_active: bool = True


class KpiDefinitionUpdate(BaseModel):
    kpi_no: Optional[str] = None
    kpi_name: Optional[str] = None
    process_name: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    target_value: Optional[float] = None
    target_direction: Optional[Literal["HIGHER", "LOWER"]] = None
    threshold_yellow: Optional[float] = None
    threshold_red: Optional[float] = None
    measurement_frequency: Optional[Literal["DAILY", "WEEKLY", "MONTHLY", "QUARTERLY", "YEARLY"]] = None
    responsible: Optional[str] = None
    formula: Optional[str] = None
    is_active: Optional[bool] = None


class KpiDefinitionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    kpi_id: int
    kpi_no: str
    kpi_name: str
    process_name: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    target_value: Optional[float] = None
    target_direction: str
    threshold_yellow: Optional[float] = None
    threshold_red: Optional[float] = None
    measurement_frequency: str
    responsible: Optional[str] = None
    formula: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    latest_value: Optional[float] = None
    latest_status: Optional[str] = None


# ============================================================
# KPI 데이터 (Data)
# ============================================================

class KpiDataCreate(BaseModel):
    period: str                              # e.g. '2026-01'
    actual_value: float
    remarks: Optional[str] = None
    collected_by: Optional[str] = None


class KpiDataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    data_id: int
    kpi_id: int
    period: str
    actual_value: float
    status: str                              # GREEN / YELLOW / RED (auto-calculated)
    remarks: Optional[str] = None
    collected_by: Optional[str] = None
    collected_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    kpi_name: Optional[str] = None


# ============================================================
# KPI 대시보드
# ============================================================

class KpiDashboardItem(BaseModel):
    kpi_id: int
    kpi_no: str
    kpi_name: str
    category: Optional[str] = None
    unit: Optional[str] = None
    target_value: Optional[float] = None
    target_direction: str
    latest_value: Optional[float] = None
    latest_status: Optional[str] = None      # GREEN / YELLOW / RED
    trend: Optional[List[float]] = None      # last 6 values


# ============================================================
# 공정 모니터링
# ============================================================

class ProcessMonitorCreate(BaseModel):
    process_name: str
    monitor_date: date
    monitor_type: str = "ROUTINE"            # ROUTINE / SPECIAL / LAYERED
    auditor: Optional[str] = None
    result: str = "OK"                       # OK / NG / NA
    score: Optional[float] = None
    findings: Optional[str] = None
    actions_required: Optional[str] = None
    status: str = "OPEN"                     # OPEN / IN_PROGRESS / CLOSED


class ProcessMonitorUpdate(BaseModel):
    process_name: Optional[str] = None
    monitor_date: Optional[date] = None
    monitor_type: Optional[str] = None
    auditor: Optional[str] = None
    result: Optional[str] = None
    score: Optional[float] = None
    findings: Optional[str] = None
    actions_required: Optional[str] = None
    status: Optional[str] = None


class ProcessMonitorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    monitor_id: int
    process_name: str
    monitor_date: date
    monitor_type: str
    auditor: Optional[str] = None
    result: str
    score: Optional[float] = None
    findings: Optional[str] = None
    actions_required: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ============================================================
# 리스크/이슈
# ============================================================

class RiskIssueCreate(BaseModel):
    issue_no: str
    issue_type: Literal["RISK", "OPPORTUNITY", "ISSUE"]
    category: Optional[str] = None
    process_name: Optional[str] = None
    description: str
    severity: int = Field(default=3, ge=1, le=5)
    likelihood: int = Field(default=3, ge=1, le=5)
    mitigation_plan: Optional[str] = None
    responsible: Optional[str] = None
    target_date: Optional[date] = None
    status: Literal["IDENTIFIED", "ANALYZING", "MITIGATING", "CLOSED", "ACCEPTED"] = "IDENTIFIED"


class RiskIssueUpdate(BaseModel):
    issue_no: Optional[str] = None
    issue_type: Optional[Literal["RISK", "OPPORTUNITY", "ISSUE"]] = None
    category: Optional[str] = None
    process_name: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[int] = Field(default=None, ge=1, le=5)
    likelihood: Optional[int] = Field(default=None, ge=1, le=5)
    mitigation_plan: Optional[str] = None
    responsible: Optional[str] = None
    target_date: Optional[date] = None
    status: Optional[Literal["IDENTIFIED", "ANALYZING", "MITIGATING", "CLOSED", "ACCEPTED"]] = None


class RiskIssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    issue_id: int
    issue_no: str
    issue_type: str
    category: Optional[str] = None
    process_name: Optional[str] = None
    description: str
    severity: int
    likelihood: int
    risk_score: Optional[int] = None         # severity * likelihood (auto-calculated)
    mitigation_plan: Optional[str] = None
    responsible: Optional[str] = None
    target_date: Optional[date] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
