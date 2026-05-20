"""
규격관리 Pydantic 스키마
"""

from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Literal, Optional


# ============================================================
# 규격 마스터
# ============================================================

class SpecificationCreate(BaseModel):
    spec_no: str
    spec_type: Literal["CUSTOMER", "DRAWING", "LEGAL", "INTERNAL"] = "CUSTOMER"
    customer_id: Optional[str] = None
    product_id: Optional[str] = None
    title: str
    revision: int = 1
    status: str = "ACTIVE"  # ACTIVE/SUPERSEDED/OBSOLETE
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    source: Optional[str] = None
    remarks: Optional[str] = None


class SpecificationUpdate(BaseModel):
    spec_type: Optional[Literal["CUSTOMER", "DRAWING", "LEGAL", "INTERNAL"]] = None
    customer_id: Optional[str] = None
    product_id: Optional[str] = None
    title: Optional[str] = None
    revision: Optional[int] = None
    status: Optional[str] = None
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    source: Optional[str] = None
    remarks: Optional[str] = None


class SpecificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    spec_mgmt_id: int
    spec_no: str
    spec_type: str
    customer_id: Optional[str] = None
    product_id: Optional[str] = None
    title: str
    revision: int
    status: str
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    source: Optional[str] = None
    remarks: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    drawing_count: Optional[int] = None


# ============================================================
# 도면 개정이력
# ============================================================

class DrawingRevisionCreate(BaseModel):
    drawing_no: str
    revision_no: int
    change_summary: Optional[str] = None
    changed_by: Optional[str] = None
    change_date: Optional[date] = None
    file_path: Optional[str] = None


class DrawingRevisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    drawing_rev_id: int
    spec_mgmt_id: int
    drawing_no: str
    revision_no: int
    change_summary: Optional[str] = None
    changed_by: Optional[str] = None
    change_date: Optional[date] = None
    file_path: Optional[str] = None
    created_at: Optional[datetime] = None


# ============================================================
# SI FAQ
# ============================================================

class SiFaqCreate(BaseModel):
    customer_id: Optional[str] = None
    category: Optional[str] = None
    question: str
    answer: Optional[str] = None
    reference_spec_id: Optional[int] = None
    is_active: bool = True


class SiFaqUpdate(BaseModel):
    customer_id: Optional[str] = None
    category: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    reference_spec_id: Optional[int] = None
    is_active: Optional[bool] = None


class SiFaqResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    faq_id: int
    customer_id: Optional[str] = None
    category: Optional[str] = None
    question: str
    answer: Optional[str] = None
    reference_spec_id: Optional[int] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ============================================================
# CSR (고객 특별요구사항)
# ============================================================

class CsrCreate(BaseModel):
    csr_no: str
    customer_id: Optional[str] = None
    requirement: str
    category: Optional[str] = None  # 품질/포장/물류/환경
    iatf_clause: Optional[str] = None
    compliance_status: Literal["PENDING", "COMPLIANT", "NON_COMPLIANT", "NA"] = "PENDING"
    responsible: Optional[str] = None
    target_date: Optional[date] = None
    evidence: Optional[str] = None


class CsrUpdate(BaseModel):
    customer_id: Optional[str] = None
    requirement: Optional[str] = None
    category: Optional[str] = None
    iatf_clause: Optional[str] = None
    compliance_status: Optional[Literal["PENDING", "COMPLIANT", "NON_COMPLIANT", "NA"]] = None
    responsible: Optional[str] = None
    target_date: Optional[date] = None
    completion_date: Optional[date] = None
    evidence: Optional[str] = None


class CsrResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    csr_id: int
    csr_no: str
    customer_id: Optional[str] = None
    requirement: str
    category: Optional[str] = None
    iatf_clause: Optional[str] = None
    compliance_status: str
    responsible: Optional[str] = None
    target_date: Optional[date] = None
    completion_date: Optional[date] = None
    evidence: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
