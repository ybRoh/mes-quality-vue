"""
고객심사관리 Pydantic 스키마
- CustomerAudit, CustomerAuditFinding, CustomerAuditAction Create/Update/Response
"""

from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Literal, Optional


# ============================================================
# 고객심사
# ============================================================

class CustomerAuditCreate(BaseModel):
    audit_no: str
    customer_id: Optional[str] = None
    audit_type: Literal["SQ", "PROCESS", "PRODUCT", "SYSTEM"] = "SQ"
    audit_date: Optional[date] = None
    audit_end_date: Optional[date] = None
    auditor_name: Optional[str] = None
    scope: Optional[str] = None
    result: Literal["PENDING", "PASS", "CONDITIONAL", "FAIL"] = "PENDING"
    score: Optional[float] = None
    status: Literal["SCHEDULED", "IN_PROGRESS", "COMPLETED", "CLOSED"] = "SCHEDULED"
    remarks: Optional[str] = None


class CustomerAuditUpdate(BaseModel):
    customer_id: Optional[str] = None
    audit_type: Optional[Literal["SQ", "PROCESS", "PRODUCT", "SYSTEM"]] = None
    audit_date: Optional[date] = None
    audit_end_date: Optional[date] = None
    auditor_name: Optional[str] = None
    scope: Optional[str] = None
    result: Optional[Literal["PENDING", "PASS", "CONDITIONAL", "FAIL"]] = None
    score: Optional[float] = None
    status: Optional[Literal["SCHEDULED", "IN_PROGRESS", "COMPLETED", "CLOSED"]] = None
    remarks: Optional[str] = None


class CustomerAuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cust_audit_id: int
    audit_no: str
    customer_id: Optional[str] = None
    audit_type: str
    audit_date: Optional[date] = None
    audit_end_date: Optional[date] = None
    auditor_name: Optional[str] = None
    scope: Optional[str] = None
    result: str
    score: Optional[float] = None
    status: str
    remarks: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    finding_count: Optional[int] = None


# ============================================================
# 고객심사 발견사항
# ============================================================

class CustomerAuditFindingCreate(BaseModel):
    finding_no: str
    finding_type: Literal["MAJOR_NC", "MINOR_NC", "OBSERVATION", "OFI"]
    clause_ref: Optional[str] = None
    description: str
    evidence: Optional[str] = None
    status: Literal["OPEN", "ACTION_REQUIRED", "IN_PROGRESS", "CLOSED", "VERIFIED"] = "OPEN"


class CustomerAuditFindingUpdate(BaseModel):
    finding_type: Optional[Literal["MAJOR_NC", "MINOR_NC", "OBSERVATION", "OFI"]] = None
    clause_ref: Optional[str] = None
    description: Optional[str] = None
    evidence: Optional[str] = None
    status: Optional[Literal["OPEN", "ACTION_REQUIRED", "IN_PROGRESS", "CLOSED", "VERIFIED"]] = None


class CustomerAuditFindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cust_finding_id: int
    cust_audit_id: int
    finding_no: str
    finding_type: str
    clause_ref: Optional[str] = None
    description: str
    evidence: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    action_count: Optional[int] = None
    audit_no: Optional[str] = None


# ============================================================
# 고객심사 시정조치
# ============================================================

class CustomerAuditActionCreate(BaseModel):
    action_no: str
    root_cause: Optional[str] = None
    containment_action: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    responsible: Optional[str] = None
    target_date: Optional[date] = None
    status: Literal["OPEN", "IN_PROGRESS", "COMPLETED", "VERIFIED"] = "OPEN"


class CustomerAuditActionUpdate(BaseModel):
    root_cause: Optional[str] = None
    containment_action: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    responsible: Optional[str] = None
    target_date: Optional[date] = None
    completion_date: Optional[date] = None
    status: Optional[Literal["OPEN", "IN_PROGRESS", "COMPLETED", "VERIFIED"]] = None


class CustomerAuditActionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cust_action_id: int
    cust_finding_id: int
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
    customer_feedback: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    finding_no: Optional[str] = None
    is_overdue: Optional[bool] = None


# ============================================================
# 고객심사 연간 요약
# ============================================================

class CustomerAuditSummaryResponse(BaseModel):
    audit_year: int
    total_audits: int
    pass_count: int
    conditional_count: int
    fail_count: int
    total_findings: int
    major_nc_count: int
    minor_nc_count: int
    observation_count: int
    total_actions: int
    completed_actions: int
    overdue_actions: int
