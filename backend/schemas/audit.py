"""
내부심사관리 Pydantic 스키마
- AuditRequirement, AuditPlan, AuditFinding, CorrectiveAction Create/Update/Response
"""

from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Literal, Optional


# ============================================================
# SQ 요구사항
# ============================================================

class AuditRequirementCreate(BaseModel):
    req_no: str
    clause_ref: Optional[str] = None
    category: Optional[str] = None
    description: str
    audit_criteria: Optional[str] = None
    is_active: bool = True


class AuditRequirementUpdate(BaseModel):
    clause_ref: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    audit_criteria: Optional[str] = None
    is_active: Optional[bool] = None


class AuditRequirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    req_id: int
    req_no: str
    clause_ref: Optional[str] = None
    category: Optional[str] = None
    description: str
    audit_criteria: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ============================================================
# 심사 계획
# ============================================================

class AuditPlanCreate(BaseModel):
    plan_no: str
    audit_year: int
    audit_type: Literal["INTERNAL", "EXTERNAL", "SUPPLIER"] = "INTERNAL"
    title: str
    scope: Optional[str] = None
    department: Optional[str] = None
    lead_auditor: Optional[str] = None
    plan_start: Optional[date] = None
    plan_end: Optional[date] = None
    status: Literal["PLANNED", "IN_PROGRESS", "COMPLETED", "CANCELLED"] = "PLANNED"


class AuditPlanUpdate(BaseModel):
    audit_year: Optional[int] = None
    audit_type: Optional[Literal["INTERNAL", "EXTERNAL", "SUPPLIER"]] = None
    title: Optional[str] = None
    scope: Optional[str] = None
    department: Optional[str] = None
    lead_auditor: Optional[str] = None
    plan_start: Optional[date] = None
    plan_end: Optional[date] = None
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None
    status: Optional[Literal["PLANNED", "IN_PROGRESS", "COMPLETED", "CANCELLED"]] = None


class AuditPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plan_id: int
    plan_no: str
    audit_year: int
    audit_type: str
    title: str
    scope: Optional[str] = None
    department: Optional[str] = None
    lead_auditor: Optional[str] = None
    plan_start: Optional[date] = None
    plan_end: Optional[date] = None
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    finding_count: Optional[int] = None


# ============================================================
# 부적합/관찰
# ============================================================

class AuditFindingCreate(BaseModel):
    finding_no: str
    finding_type: Literal["MAJOR_NC", "MINOR_NC", "OBSERVATION", "OFI"]
    clause_ref: Optional[str] = None
    description: str
    evidence: Optional[str] = None
    status: Literal["OPEN", "ACTION_REQUIRED", "IN_PROGRESS", "CLOSED", "VERIFIED"] = "OPEN"


class AuditFindingUpdate(BaseModel):
    finding_type: Optional[Literal["MAJOR_NC", "MINOR_NC", "OBSERVATION", "OFI"]] = None
    clause_ref: Optional[str] = None
    description: Optional[str] = None
    evidence: Optional[str] = None
    status: Optional[Literal["OPEN", "ACTION_REQUIRED", "IN_PROGRESS", "CLOSED", "VERIFIED"]] = None


class AuditFindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    finding_id: int
    plan_id: int
    finding_no: str
    finding_type: str
    clause_ref: Optional[str] = None
    description: str
    evidence: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    action_count: Optional[int] = None
    plan_no: Optional[str] = None


# ============================================================
# 시정조치
# ============================================================

class CorrectiveActionCreate(BaseModel):
    action_no: str
    root_cause: Optional[str] = None
    containment_action: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    responsible: Optional[str] = None
    target_date: Optional[date] = None
    status: Literal["OPEN", "IN_PROGRESS", "COMPLETED", "VERIFIED"] = "OPEN"


class CorrectiveActionUpdate(BaseModel):
    root_cause: Optional[str] = None
    containment_action: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    responsible: Optional[str] = None
    target_date: Optional[date] = None
    completion_date: Optional[date] = None
    status: Optional[Literal["OPEN", "IN_PROGRESS", "COMPLETED", "VERIFIED"]] = None


class CorrectiveActionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    action_id: int
    finding_id: int
    action_no: str
    root_cause: Optional[str] = None
    containment_action: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    responsible: Optional[str] = None
    target_date: Optional[date] = None
    completion_date: Optional[date] = None
    status: str
    verified_by: Optional[str] = None
    verified_date: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    finding_no: Optional[str] = None
    is_overdue: Optional[bool] = None


# ============================================================
# 심사 연간 요약
# ============================================================

class AuditSummaryResponse(BaseModel):
    audit_year: int
    total_plans: int
    completed_plans: int
    total_findings: int
    major_nc_count: int
    minor_nc_count: int
    observation_count: int
    ofi_count: int
    total_actions: int
    completed_actions: int
    overdue_actions: int
