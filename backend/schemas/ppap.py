"""
PPAP (생산부품승인절차) Pydantic 스키마
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


class PpapCreate(BaseModel):
    """PPAP 생성 요청"""
    ppap_no: str
    product_id: str
    customer_id: Optional[str] = None
    submission_level: int = 3
    reason: Optional[str] = None
    status: str = "PLANNING"
    fmea_id: Optional[int] = None
    cp_id: Optional[int] = None
    msa_id: Optional[int] = None
    apqp_id: Optional[int] = None


class PpapUpdate(BaseModel):
    """PPAP 수정 요청"""
    product_id: Optional[str] = None
    customer_id: Optional[str] = None
    submission_level: Optional[int] = None
    reason: Optional[str] = None
    status: Optional[str] = None
    fmea_id: Optional[int] = None
    cp_id: Optional[int] = None
    msa_id: Optional[int] = None
    apqp_id: Optional[int] = None


class PpapResponse(BaseModel):
    """PPAP 응답"""
    model_config = ConfigDict(from_attributes=True)

    ppap_id: int
    ppap_no: str
    product_id: str
    customer_id: Optional[str] = None
    submission_level: int
    reason: Optional[str] = None
    status: str
    fmea_id: Optional[int] = None
    cp_id: Optional[int] = None
    msa_id: Optional[int] = None
    apqp_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    product_name: Optional[str] = None
    customer_name: Optional[str] = None
    completeness_pct: Optional[float] = None


class PpapElementCreate(BaseModel):
    """PPAP 요소 생성"""
    element_no: int
    element_name: str
    is_required: int = 1
    status: str = "NOT_STARTED"
    document_ref: Optional[str] = None


class PpapElementUpdate(BaseModel):
    """PPAP 요소 수정"""
    element_name: Optional[str] = None
    is_required: Optional[int] = None
    status: Optional[str] = None
    document_ref: Optional[str] = None


class PpapElementResponse(BaseModel):
    """PPAP 요소 응답"""
    model_config = ConfigDict(from_attributes=True)

    element_id: int
    ppap_id: int
    element_no: int
    element_name: str
    is_required: int
    status: str
    document_ref: Optional[str] = None


class PpapCompletenessResponse(BaseModel):
    """PPAP 완성도 응답"""
    ppap_id: int
    total_elements: int
    required_elements: int
    completed_elements: int
    completeness_pct: float
    elements: List[PpapElementResponse]
