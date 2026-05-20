"""
교육/자격관리 Pydantic 스키마
- TrainingCourse, TrainingRecord, Qualification, CompetencyMatrix, QualAudit Create/Update/Response
"""

from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import Literal, Optional, List


# ============================================================
# 교육과정 마스터
# ============================================================

class TrainingCourseCreate(BaseModel):
    course_no: str
    course_name: str
    category: Optional[str] = None
    duration_hours: Optional[float] = None
    training_type: Literal["INTERNAL", "EXTERNAL", "OJT", "ONLINE"] = "INTERNAL"
    recurrence_months: Optional[int] = None
    is_active: bool = True


class TrainingCourseUpdate(BaseModel):
    course_name: Optional[str] = None
    category: Optional[str] = None
    duration_hours: Optional[float] = None
    training_type: Optional[Literal["INTERNAL", "EXTERNAL", "OJT", "ONLINE"]] = None
    recurrence_months: Optional[int] = None
    is_active: Optional[bool] = None


class TrainingCourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    course_id: int
    course_no: str
    course_name: str
    category: Optional[str] = None
    duration_hours: Optional[float] = None
    training_type: str
    recurrence_months: Optional[int] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    record_count: Optional[int] = None


# ============================================================
# 교육이수 기록
# ============================================================

class TrainingRecordCreate(BaseModel):
    course_id: int
    trainee_id: str
    training_date: date
    score: Optional[float] = None
    result: Literal["PENDING", "PASS", "FAIL"] = "PENDING"
    next_due_date: Optional[date] = None


class TrainingRecordBulkCreate(BaseModel):
    course_id: int
    training_date: date
    trainee_ids: List[str]
    score: Optional[float] = None
    result: Literal["PENDING", "PASS", "FAIL"] = "PASS"


class TrainingRecordUpdate(BaseModel):
    training_date: Optional[date] = None
    score: Optional[float] = None
    result: Optional[Literal["PENDING", "PASS", "FAIL"]] = None
    next_due_date: Optional[date] = None


class TrainingRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    record_id: int
    course_id: int
    trainee_id: str
    training_date: date
    score: Optional[float] = None
    result: str
    next_due_date: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    course_name: Optional[str] = None
    course_no: Optional[str] = None


# ============================================================
# 자격/인증
# ============================================================

class QualificationCreate(BaseModel):
    qual_type: Literal["INTERNAL_AUDITOR", "EXTERNAL_AUDITOR", "WELDER", "NDT", "OTHER"]
    qual_name: str
    holder_id: str
    issuing_body: Optional[str] = None
    certificate_no: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: Literal["ACTIVE", "EXPIRED", "SUSPENDED", "REVOKED"] = "ACTIVE"


class QualificationUpdate(BaseModel):
    qual_type: Optional[Literal["INTERNAL_AUDITOR", "EXTERNAL_AUDITOR", "WELDER", "NDT", "OTHER"]] = None
    qual_name: Optional[str] = None
    holder_id: Optional[str] = None
    issuing_body: Optional[str] = None
    certificate_no: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: Optional[Literal["ACTIVE", "EXPIRED", "SUSPENDED", "REVOKED"]] = None


class QualificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    qual_id: int
    qual_type: str
    qual_name: str
    holder_id: str
    issuing_body: Optional[str] = None
    certificate_no: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    days_until_expiry: Optional[int] = None
    audit_count: Optional[int] = None


# ============================================================
# 역량 매트릭스
# ============================================================

class CompetencyMatrixCreate(BaseModel):
    employee_id: str
    skill_name: str
    required_level: int = Field(1, ge=1, le=5)
    current_level: int = Field(0, ge=0, le=5)
    evaluation_date: Optional[date] = None
    evaluator: Optional[str] = None


class CompetencyMatrixUpdate(BaseModel):
    required_level: Optional[int] = Field(None, ge=1, le=5)
    current_level: Optional[int] = Field(None, ge=0, le=5)
    evaluation_date: Optional[date] = None
    evaluator: Optional[str] = None


class CompetencyMatrixResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    matrix_id: int
    employee_id: str
    skill_name: str
    required_level: int
    current_level: int
    gap: Optional[int] = None
    evaluation_date: Optional[date] = None
    evaluator: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class GapAnalysisResponse(BaseModel):
    employee_id: str
    total_skills: int
    avg_gap: float
    max_gap: int
    skills_with_gap: int
    skills_met: int


# ============================================================
# 자격심사 기록
# ============================================================

class QualAuditCreate(BaseModel):
    qual_id: int
    audit_date: date
    auditor: Optional[str] = None
    result: Literal["PASS", "FAIL", "CONDITIONAL"] = "PASS"
    score: Optional[float] = None
    next_audit_date: Optional[date] = None
    remarks: Optional[str] = None


class QualAuditUpdate(BaseModel):
    audit_date: Optional[date] = None
    auditor: Optional[str] = None
    result: Optional[Literal["PASS", "FAIL", "CONDITIONAL"]] = None
    score: Optional[float] = None
    next_audit_date: Optional[date] = None
    remarks: Optional[str] = None


class QualAuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    qual_audit_id: int
    qual_id: int
    audit_date: date
    auditor: Optional[str] = None
    result: str
    score: Optional[float] = None
    next_audit_date: Optional[date] = None
    remarks: Optional[str] = None
    created_at: Optional[datetime] = None
    qual_name: Optional[str] = None
    holder_id: Optional[str] = None
