"""
APQP (사전품질계획) Pydantic 스키마
"""

from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional, List


class ApqpProjectCreate(BaseModel):
    """APQP 프로젝트 생성 요청"""
    product_id: str
    customer_id: Optional[str] = None
    project_name: str
    project_no: Optional[str] = None
    current_phase: int = 1
    sop_date: Optional[date] = None
    team_leader: Optional[str] = None
    status: str = "NOT_STARTED"


class ApqpProjectUpdate(BaseModel):
    """APQP 프로젝트 수정 요청"""
    product_id: Optional[str] = None
    customer_id: Optional[str] = None
    project_name: Optional[str] = None
    current_phase: Optional[int] = None
    sop_date: Optional[date] = None
    team_leader: Optional[str] = None
    status: Optional[str] = None


class ApqpProjectResponse(BaseModel):
    """APQP 프로젝트 응답"""
    model_config = ConfigDict(from_attributes=True)

    apqp_id: int
    product_id: str
    customer_id: Optional[str] = None
    project_name: str
    project_no: Optional[str] = None
    current_phase: int
    sop_date: Optional[date] = None
    team_leader: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    product_name: Optional[str] = None
    customer_name: Optional[str] = None
    phase_count: Optional[int] = None


class ApqpPhaseCreate(BaseModel):
    """APQP 단계 생성"""
    phase_no: int
    phase_name: str
    plan_start: Optional[date] = None
    plan_end: Optional[date] = None
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None
    status: str = "NOT_STARTED"
    gate_review: Optional[str] = None


class ApqpPhaseUpdate(BaseModel):
    """APQP 단계 수정"""
    phase_name: Optional[str] = None
    plan_start: Optional[date] = None
    plan_end: Optional[date] = None
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None
    status: Optional[str] = None
    gate_review: Optional[str] = None


class ApqpPhaseResponse(BaseModel):
    """APQP 단계 응답"""
    model_config = ConfigDict(from_attributes=True)

    phase_id: int
    apqp_id: int
    phase_no: int
    phase_name: str
    plan_start: Optional[date] = None
    plan_end: Optional[date] = None
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None
    status: str
    gate_review: Optional[str] = None
    deliverable_count: Optional[int] = None


class ApqpDeliverableCreate(BaseModel):
    """APQP 산출물 생성"""
    item_name: str
    responsible: Optional[str] = None
    due_date: Optional[date] = None
    status: str = "NOT_STARTED"
    completion_date: Optional[date] = None


class ApqpDeliverableUpdate(BaseModel):
    """APQP 산출물 수정"""
    item_name: Optional[str] = None
    responsible: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[str] = None
    completion_date: Optional[date] = None


class ApqpDeliverableResponse(BaseModel):
    """APQP 산출물 응답"""
    model_config = ConfigDict(from_attributes=True)

    deliverable_id: int
    phase_id: int
    item_name: str
    responsible: Optional[str] = None
    due_date: Optional[date] = None
    status: str
    completion_date: Optional[date] = None


class GanttItem(BaseModel):
    """Gantt 차트 데이터 항목"""
    phase_no: int
    phase_name: str
    plan_start: Optional[date] = None
    plan_end: Optional[date] = None
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None
    status: str
    progress_pct: float = 0.0
